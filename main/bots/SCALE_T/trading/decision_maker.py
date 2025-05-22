import queue
import threading
import asyncio
import sys
from typing import Tuple
from datetime import datetime as dt, timezone
import time

from alpaca.trading.enums import OrderStatus, OrderType, OrderSide
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.models import Order 
from alpaca.trading.stream import TradingStream
from alpaca.data.live.stock import StockDataStream
from alpaca.data.enums import DataFeed
from alpaca.data.models.trades import Trade
from alpaca.trading import TradeUpdate

from ..common.logging_config import get_logger
from ..common.notify import send_notification
from ..common.constants import TradingType

from ..csv_utils.csv_service import CSVService

from .constants import MessageType, OrderState

from ....utils.redis import ( 
    RedisSubscriber, RedisPublisher, CHANNELS, REDIS_HOST_DOCKER, REDIS_PORT, REDIS_DB
)

class DecisionMaker:
    def __init__(self, csv_service, alpaca_interface):
        self.logger = get_logger("decision_maker")
        self.logger.info(f"Initializing DecisionMaker for {csv_service.ticker}")
        self.csv_service: CSVService = csv_service
        self.alpaca_interface = alpaca_interface
        self.action_queue = queue.Queue()
        self.producer_thread = None
        self.publisher = None
        self.last_manual_update_time = 0  # Timestamp of last manual order update
        self.manual_update_interval_sec = 10

        self.logger.info(f"Initializing pending order variables.")
        pending_order_info = self.csv_service.get_pending_order_info()
        if pending_order_info:
            order_id = pending_order_info["order_id"]
            if order_id is not None: #Check if order_id is None
                self.logger.info(f"Pending order found: {order_id} at index {pending_order_info['index']}")
                self.pending_order = self.alpaca_interface.get_order_by_id(order_id)
                self.pending_order_index = pending_order_info["index"]
                self.logger.info(f"Pending order initialized: {self.pending_order}. Handling order update.")
                self.handle_order_update(self.pending_order)
                self.order_state = OrderState.BUYING if self.pending_order.side == OrderSide.BUY else OrderState.SELLING
            else:
                self.logger.error("Pending order found but order_id is None. Exciting")
                sys.exit()
        else:
            self.logger.debug("No pending order found.")
            self.pending_order = None
            self.pending_order_index = None
            self.order_state = OrderState.NONE

        # Get initial price and put it on the queue
        self.logger.info("Getting initial price and putting it on the queue.")
        current_price = self.alpaca_interface.get_current_price()
        self._prev_price = current_price
        self.action_queue.put({'type': 'price_update', 'data': current_price})

        self.logger.info("Checking share count.")
        # self._check_share_count()


    def _check_share_count(self):
        alpaca_shares = self.alpaca_interface.get_shares_count()
        csv_shares = self.csv_service.get_current_held_shares()
        if alpaca_shares != csv_shares:
            self.logger.error(f"Mismatch in shares: Alpaca ({alpaca_shares}) vs CSV ({csv_shares}). Exiting.")
            sys.exit()
        self.logger.info(f"Shares count verified: Alpaca ({alpaca_shares}) vs CSV ({csv_shares})")

    def handle_order_update(self, order: Order):
        if not self.pending_order:
            self.logger.warning("THERE IS NO ORDER TO WARRRANT AN ORDER UPDATE. Can't update. POSSIBLE BUG OR DUPLICATE ORDER UPDATE")
            return
        if self.pending_order.id != order.id:
            self.logger.warning(f"Mismatch. Current pid:{self.pending_order.id}, update_pid:{order.id}")
            self.logger.warning("Dropping order update")
            return
        self.logger.debug(f"Handling order update. Current pending order is {self.pending_order}")
        self.logger.debug(f"Incoming order {order}")
        self.logger.debug(f"At index {self.pending_order_index} of type {type(self.pending_order_index)}")
        status = order.status
        filled_qty = float(order.filled_qty)
        filled_avg_price = float(order.filled_avg_price) if order.filled_avg_price is not None else None 
        side = order.side 
        self.logger.info(f"Handling order update. Order status: {status}, Order ID: {order.id}")
        if status == OrderStatus.FILLED:
            self.logger.info("Order filled")
            self.logger.info(f"Order status: FILLED. Filled quantity: {filled_qty}, Filled average price: {filled_avg_price}, Order side: {side}")

            profits = self.csv_service.update_order_status(
                self.pending_order_index, filled_qty, filled_avg_price, side
            )
            self.pending_order = None
            self.pending_order_index = None
            self.order_state = OrderState.NONE
            self.logger.info("Order filled and handled successfully. Checking share count.")
            self._check_share_count()

            profits['symbol'] = self.csv_service.ticker
            profits['timestamp'] = dt.now(timezone.utc).isoformat()
            self.publisher.publish(CHANNELS.PROFIT_REPORT, message_data=profits, sender='scale_t')
            self.logger.info(f"Profit report published: {profits}")

        elif status in (OrderStatus.CANCELED, OrderStatus.EXPIRED):
            self.logger.info("Order cancelled or expired")
            self.logger.info(f"Order status: {status}. Filled quantity: {filled_qty}, Filled average price: {filled_avg_price}, Order side: {side}")
            #input("Approve CANCELED/EXPIRED order handling? (press Enter to continue)")
            self.csv_service.update_order_status(self.pending_order_index, filled_qty, filled_avg_price, side)
            # Clear pending_order_id in CSV
            row = self.csv_service.get_row_by_index(self.pending_order_index)
            if row:
                row['pending_order_id'] = "None"
                self.csv_service.save()
                
            # Reset pending order variables
            self.pending_order = None
            self.pending_order_index = None
            self.order_state = OrderState.NONE

            self.logger.info("Checking share count after order reset.")
            self._check_share_count()

        elif status in (
            OrderStatus.ACCEPTED,
            OrderStatus.NEW,
            OrderStatus.PARTIALLY_FILLED,
            OrderStatus.PENDING_NEW,
            OrderStatus.PENDING_CANCEL,
        ):
            self.logger.info("Order pending")
            self.logger.info(f"Order status: PENDING. Status: {status}")
        else:
            self.logger.error(f"Unexpected order status: {status}. Exiting.")
            sys.exit()

    def _check_cancel_order(self, current_price):
        if self.pending_order:
            order_price = 0
            if self.pending_order.order_type == OrderType.MARKET:
                associated_csv_line = self.csv_service.get_row_by_index(self.pending_order_index)
                if self.pending_order.side == 'buy':
                    order_price = associated_csv_line["buy_price"]
                else :
                    order_price = associated_csv_line["sell_price"]
            else :
                order_price = self.pending_order.limit_price
            if self.pending_order.side == 'buy' and current_price >= float(order_price) * 1.0025:
                self.logger.info(f"Decision: Cancelling buy order. Order ID: {self.pending_order.id}, Expected price: {order_price}, Current price: {current_price}")
                send_notification("Bot needs help", "SomeDetails")
                #input("Approve buy order cancellation? (press Enter to continue)")
                cancel_success = self.alpaca_interface.cancel_order(self.pending_order.id)
                self.order_state = OrderState.CANCELLING
                if not cancel_success:
                    self.logger.warning(f"Failed to cancel buy order ID: {self.pending_order.id}, manually triggering order update")
                    # Manually trigger order update in the queue to catch any missed updates
                    self._trigger_manual_order_update()
                    return True  # Still indicate cancellation was attempted
                self.logger.info(f"Cancelled buy order due to price increase. Order ID: {self.pending_order.id}")
                return True  # Indicate that a cancellation occurred
            elif self.pending_order.side == 'sell' and current_price <= float(order_price) * 0.9975:
                self.logger.info(f"Decision: Cancelling sell order. Order ID: {self.pending_order.id}, Expected price: {order_price}, Current price: {current_price}")
                send_notification("Bot needs help", "SomeDetails")
                #input("Approve sell order cancellation? (press Enter to continue)")
                cancel_success = self.alpaca_interface.cancel_order(self.pending_order.id)
                self.order_state = OrderState.CANCELLING
                if not cancel_success:
                    self.logger.warning(f"Failed to cancel sell order ID: {self.pending_order.id}, manually triggering order update")
                    # Manually trigger order update in the queue to catch any missed updates
                    self._trigger_manual_order_update()
                    return True  # Still indicate cancellation was attempted
                self.logger.info(f"Cancelled sell order due to price decrease. Order ID: {self.pending_order.id}")
                return True  # Indicate that a cancellation occurred
        return False
        
    def _trigger_manual_order_update(self):
        """Manually trigger an order update to catch any missed updates.
        
        Only triggers the update once per minute to avoid excessive updates.
        Uses direct Alpaca objects and places them in the queue for consistent handling.
        """
        current_time = time.time()
        # Check if it's been at least 10 seconds since the last manual update
        if current_time - self.last_manual_update_time < self.manual_update_interval_sec:
            self.logger.info(f"Skipping manual order update - last update was less than a {self.manual_update_interval_sec} secs ago")
            return
            
        if self.pending_order:
            # Refresh the order data from Alpaca
            try:
                # Get the latest order directly from Alpaca
                latest_order = self.alpaca_interface.get_order_by_id(self.pending_order.id)
                
                # Create a proper TradeUpdate object that matches what comes from the Alpaca stream
                trade_update = TradeUpdate(order=latest_order, event=MessageType.ORDER_UPDATE.value, timestamp=dt.now(timezone.utc))
                
                # Queue the update just like the websocket would
                self.action_queue.put({'type': MessageType.ORDER_UPDATE, 'data': trade_update, 'source': 'manual'})
                
                self.logger.info(f"Manually triggered order update for order ID: {latest_order.id}")
                self.logger.info(f"Order status: {latest_order.status}")
                
                # Update the timestamp of the last manual update
                self.last_manual_update_time = current_time
            except Exception as e:
                send_notification("Bot needs help", "Failed to manually trigger order update")
                self.logger.error(f"Failed to manually trigger order update: {e}")


    def _check_place_buy_order(self, current_price):
        rows_to_buy = self.csv_service.get_rows_for_buy(current_price)
        if rows_to_buy:
            # If we have a pending sell order but want to buy, cancel the sell order first
            if self.pending_order and self.pending_order.side == 'sell':
                self.logger.info(f"Cancelling pending sell order to place buy order. Order ID: {self.pending_order.id}")
                send_notification("Bot needs help", "SomeDetails")
                #input("Approve cancellation of sell order to place buy order? (press Enter to continue)")
                cancel_success = self.alpaca_interface.cancel_order(self.pending_order.id)
                self.order_state = OrderState.CANCELLING
                if not cancel_success:
                    self.logger.warning(f"Failed to cancel sell order ID: {self.pending_order.id} for buy placement, manually triggering order update")
                    # Manually trigger order update in the queue to catch any missed updates
                    self._trigger_manual_order_update()
                # self._refresh_pending_order()
                return True  # Return after cancellation to wait for order update
            elif self.pending_order and self.pending_order.side == 'buy':
                self.logger.debug("Pending buy order found. Skipping buy order placement.")
                return False

            self.logger.info(f"Checked to place buy order at price {current_price}")
            self.logger.debug(f"Rows to buy: {len(rows_to_buy)}")

            total_qty_to_buy = sum(float(row['target_shares']) - float(row['held_shares']) for row in rows_to_buy)
            # We need to place whole orders before fractional orders
            # Check if order amount is greater than 1 + trim the decimals and place order
            # Otherwise just place order(Covers everything less than one and whole shares off the bat)
            if total_qty_to_buy > 1 and total_qty_to_buy % 1 > 0:
                self.logger.debug(f"Wanted to buy {total_qty_to_buy} but trimming to {int(total_qty_to_buy)}")
                total_qty_to_buy = int(total_qty_to_buy)
            # Find the row with the lowest buy_price (highest index)
            row_to_buy = rows_to_buy[-1]
            buy_price = float(row_to_buy['buy_price'])
            limit_price = round(min(current_price + 0.01, buy_price), 2)
            if total_qty_to_buy < 0.01:  # Support fractional shares
                return False

            buy_has_unrealized_profit = buy_price != limit_price
            if total_qty_to_buy == 1:
                self.logger.info("Decision: Placing buy order for 1 share.")
                self.logger.info(f"Unrealized profit: {buy_has_unrealized_profit}")
                send_notification("Bot needs help", "SomeDetails")
            else:
                self.logger.info(f"Decision: Placing buy order. Quantity: {total_qty_to_buy}, Limit price: {limit_price}, Buy price: {buy_price}, Current price: {current_price}")
                self.logger.info(f"Unrealized profit: {buy_has_unrealized_profit}")
                send_notification("Bot needs help", "SomeDetails")
            try:
                order = self.alpaca_interface.place_order(OrderSide.BUY, limit_price, total_qty_to_buy)
                self.order_state = OrderState.BUYING
                if order is None:
                    self.logger.error("Failed to place buy order")
                    return False
                self.pending_order = order
                self.pending_order_index = int(row_to_buy['index'])
                row_to_buy['pending_order_id'] = order.id
                self.csv_service.save()
                self.last_manual_update_time = time.time() # keep record of when order was placed
                return True
            except Exception as e:
                self.logger.error(f"Error placing buy order: {e}")
                return False
        return False
    
    def _check_place_sell_order(self, current_price):
        rows_to_sell = self.csv_service.get_rows_for_sell(current_price)
        if rows_to_sell:
            # If we have a pending buy order but want to sell, cancel the buy order first
            if self.pending_order and self.pending_order.side == 'buy':
                self.logger.info(f"Cancelling pending buy order to place sell order. Order ID: {self.pending_order.id}")
                send_notification("Bot needs help", "SomeDetails")
                #input("Approve cancellation of buy order to place sell order? (press Enter to continue)")
                cancel_success = self.alpaca_interface.cancel_order(self.pending_order.id)
                self.order_state = OrderState.CANCELLING
                if not cancel_success:
                    self.logger.warning(f"Failed to cancel buy order ID: {self.pending_order.id} for sell placement, manually triggering order update")
                    # Manually trigger order update in the queue to catch any missed updates
                    self._trigger_manual_order_update()
                # self._refresh_pending_order()
                return True  # Return after cancellation to wait for order update
            elif self.pending_order and self.pending_order.side == 'sell':
                self.logger.debug(f"Skipping sell order as there is already a pendingOrder of sell")
                return False

            self.logger.info(f"Checked to place sell order at price {current_price}")
            self.logger.debug(f"Rows to sell: {len(rows_to_sell)}")

            total_qty_to_sell = sum(float(row['held_shares']) for row in rows_to_sell)

            if total_qty_to_sell > 1 and total_qty_to_sell % 1 > 0:
                self.logger.debug(f"Wanted to sell {total_qty_to_sell} but trimming to {int(total_qty_to_sell)}")
                total_qty_to_sell = int(total_qty_to_sell)
            row_to_sell = rows_to_sell[0]
            sell_price = float(row_to_sell['sell_price'])
            limit_price = round(max(current_price - 0.01, sell_price), 2)
            sell_has_extra_profit = sell_price != limit_price
            unrealized_profit = float(row_to_sell['unrealized_profit'])
            if total_qty_to_sell == 1 and (sell_has_extra_profit or unrealized_profit > 0):
                self.logger.info(f"Decision: Placing sell order for 1 share. Limit price: {limit_price}")
                self.logger.info(f"Extra profit: {sell_has_extra_profit}")
                self.logger.info(f"Unrealized profit: {unrealized_profit}")
                send_notification("Bot needs help", "SomeDetails")
            elif total_qty_to_sell > 1:
                self.logger.info(f"Decision: Placing sell order. Quantity: {total_qty_to_sell}, Limit price: {limit_price}, Sell price: {sell_price}, Current price: {current_price}")
                self.logger.info(f"Extra profit: {sell_has_extra_profit}")
                self.logger.info(f"Unrealized profit: {unrealized_profit}")
                send_notification("Bot needs help", "SomeDetails")
            self.logger.info("Placing sell order.")
            try:
                order = self.alpaca_interface.place_order(OrderSide.SELL, limit_price, total_qty_to_sell)
                self.order_state = OrderState.SELLING
                if order is None:
                    self.logger.error("Failed to place sell order")
                    return False
                self.pending_order = order
                self.logger.info(f"Row to sell index: {row_to_sell['index']}")
                self.pending_order_index = int(row_to_sell['index'])
                row_to_sell['pending_order_id'] = order.id
                self.csv_service.save()
                self.last_manual_update_time = time.time() # keep record of when order was placed
                return True #Indicate that we placed a sell order
            except Exception as e:
                self.logger.error(f"Error placing sell order: {e}")
                return False
        return False

    def _filter_price_data(self, price: float) -> float | None:    
        if price == self._prev_price:
            return None
        price = round(price, 2)
        self._prev_price = price
        return price

    def handle_price_update(self, price):
        if self.order_state == OrderState.CANCELLING:
            return

        current_price = self._filter_price_data(price)
        if current_price is None:
            return
        if self._check_cancel_order(current_price):
            self.logger.info("Price update handled by cancel order check.")
            return  # If order was cancelled, don't proceed further

        # print("Checking to place sell order.")
        if self._check_place_sell_order(current_price):
            self.logger.info("Price update handled by sell order check.")
            return

        # print("Checking to place buy order.")
        if self._check_place_buy_order(current_price):
            self.logger.info("Price update handled by buy order check.")
            return
        
        # At this point, we have neither a pending order nor a new order to place
        # Check to see if we need to chase lines
        if self.csv_service.is_chasable_lines(current_price):
            self.csv_service.chase_price({"current_price":current_price})

    def consume_actions(self):
        if self.publisher is None:
            self.logger.error("Publisher is not initialized. Cannot consume actions. Quitting.")
            return
        while True:
            message = self.action_queue.get()
            if message['type'] == MessageType.ORDER_UPDATE:
                self.logger.info(f"Handling order update from {message.get('source','unknown')}")
                self.handle_order_update(message['data'].order)
            elif message['type'] == 'price_update':                    
                self.handle_price_update(message['data'])
            else :
                self.logger.error(f"Recieved an unknown message with type: {message['type']}")
                self.logger.error(f"message: {message}")
            self.action_queue.task_done()

    def launch_action_producer_threads(self):
        self.producer_thread = threading.Thread(target=self._subscribe_redis_producer, daemon=True)
        self.producer_thread.start()
        self.logger.info("Started action producer threads.")

    def _subscribe_redis_producer(self):
        # Need to add price subscriber here as well
        # Create a publisher and publish subscribe to price for ticker
        self.publisher = RedisPublisher(host=REDIS_HOST_DOCKER, port=REDIS_PORT, db=REDIS_DB)
        # Publish to the Broker channel
        message = {
            'action': 'subscribe',
            'ticker': self.csv_service.ticker
        }
        self.publisher.publish(CHANNELS.BROKER_REGISTRATION, message_data=message, sender='scale_t')
        self.logger.info(f"Registered to channel {CHANNELS.BROKER_REGISTRATION} for ticker {self.csv_service.ticker}")
        # Close publisher after subscribing
        # create a subscriber
        subscriber = RedisSubscriber(host=REDIS_HOST_DOCKER, port=REDIS_PORT, db=REDIS_DB)
        # generate the name of the channel
        channel_name = CHANNELS.get_ticker_channel(self.csv_service.ticker)
        # define the handler
        def redis_handler(message):
            data = message.get('data', {})
            if data.get('type') == 'price':
                price = data.get('price', None)
                if price is not None:
                    self.action_queue.put({'type': 'price_update', 'data': float(price), 'source': 'redis'})
            if data.get('type') == 'order':
                trdUpdate = message.get('data', {}).get('order_data', {})
                order_json = trdUpdate.get('order', None)
                order = Order(**order_json)
                myTradeUpdate = TradeUpdate(order=order, event=trdUpdate.get('event', None), timestamp=dt.fromisoformat(trdUpdate.get('timestamp')))
                # Check if the message is a trade update
                self.logger.info(f"Trade update: {myTradeUpdate}")
                self.logger.info(f"Trade update event: {myTradeUpdate.event}")
                self.action_queue.put({'type': MessageType.ORDER_UPDATE, 'data': myTradeUpdate, 'source': 'redis'})
        # subscribe to the channel
        assert subscriber.subscribe(channel_name, redis_handler) == True, f"Failed to subscribe to channel {channel_name}"
        # start listening for messages
        self.logger.info(f"Subscribed to channel {channel_name}")
        subscriber.start_listening()
        self.logger.info("Starting Redis subscriber...")
