For some reason I am seeing these logs in my firebase client server:
2025-05-20 20:56:31 - FirebaseClientService - INFO - Starting Firebase Client Service
2025-05-20 20:56:31 - FirebaseClientService - INFO - Using tickers file: configs/tickers.txt
2025-05-20 20:56:31 - FirebaseClientService - INFO - Loaded 2 tickers: TSLA, DGLY
2025-05-20 20:56:31 - FirebaseClientService - INFO - No Firebase database URL found in environment, will use default based on project_id
2025-05-20 20:56:31 - FirebaseClient - INFO - Initializing Firebase Client
2025-05-20 20:56:31 - FirebaseClient - INFO - Connecting to Firebase using service account: configs/adminsdk.json
2025-05-20 20:56:31 - FirebaseClient - INFO - Using database URL: https://archer-prince-default-rtdb.firebaseio.com/
2025-05-20 20:56:31 - FirebaseClient - INFO - Successfully connected to Firebase
2025-05-20 20:56:31 - FirebaseClientService - INFO - Successfully connected to Firebase Realtime Database
2025-05-20 20:56:31 - FirebaseRedisSubscriber - INFO - Initializing FirebaseRedisSubscriber for 2 tickers
2025-05-20 20:56:31 - FirebaseRedisSubscriber - INFO - Connecting to Redis at redis:6379 (attempt 1/5)
2025-05-20 20:56:31 - FirebaseRedisSubscriber - INFO - Successfully connected to Redis
2025-05-20 20:56:31 - FirebaseRedisSubscriber - INFO - Subscribing to 2 ticker channels
2025-05-20 20:56:31 - main.utils.redis.connection - INFO - Connected to Redis at redis:6379/0
2025-05-20 20:56:31 - main.utils.redis.subscriber - INFO - Subscribed to channel: TICKER_UPDATES_TSLA
2025-05-20 20:56:31 - FirebaseRedisSubscriber - INFO - Subscribed to channel: TICKER_UPDATES_TSLA
2025-05-20 20:56:31 - main.utils.redis.subscriber - INFO - Subscribed to channel: TICKER_PERFORMANCE_TSLA
2025-05-20 20:56:31 - FirebaseRedisSubscriber - INFO - Subscribed to channel: TICKER_PERFORMANCE_TSLA
2025-05-20 20:56:31 - main.utils.redis.subscriber - INFO - Subscribed to channel: TICKER_UPDATES_DGLY
2025-05-20 20:56:31 - FirebaseRedisSubscriber - INFO - Subscribed to channel: TICKER_UPDATES_DGLY
2025-05-20 20:56:31 - main.utils.redis.subscriber - INFO - Subscribed to channel: TICKER_PERFORMANCE_DGLY
2025-05-20 20:56:31 - FirebaseRedisSubscriber - INFO - Subscribed to channel: TICKER_PERFORMANCE_DGLY
2025-05-20 20:56:31 - main.utils.redis.subscriber - INFO - Subscribed to channel: TICKER_PERFORMANCE_AGGREGATE
2025-05-20 20:56:31 - FirebaseRedisSubscriber - INFO - Subscribed to channel: TICKER_PERFORMANCE_AGGREGATE
2025-05-20 20:56:31 - FirebaseRedisSubscriber - INFO - Starting to listen for messages...
2025-05-20 20:56:31 - main.utils.redis.subscriber - INFO - Starting message listener (background thread)
2025-05-20 20:56:31 - FirebaseRedisSubscriber - INFO - Listening for messages on all channels
2025-05-20 20:56:31 - FirebaseClientService - INFO - Firebase Client Service is running. Press Ctrl+C to exit.
2025-05-20 20:59:04 - FirebaseRedisSubscriber - WARNING - Received message on unknown channel: 
2025-05-20 20:59:10 - FirebaseRedisSubscriber - WARNING - Received message on unknown channel: 
2025-05-20 20:59:10 - FirebaseRedisSubscriber - WARNING - Received message on unknown channel: 
2025-05-20 20:59:51 - FirebaseRedisSubscriber - WARNING - Received message on unknown channel: 
2025-05-20 20:59:51 - FirebaseRedisSubscriber - WARNING - Received message on unknown channel: 
2025-05-20 20:59:51 - FirebaseRedisSubscriber - WARNING - Received message on unknown channel:


These are the other logs from the other containers:
scale_t_bot_tsla  | DEBUG:SCALE_T.decision_maker:At index 10 of type <class 'int'>
scale_t_bot_tsla  | 2025-05-20 20:59:10,014 - SCALE_T.decision_maker - INFO - Trade update event: new
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Trade update event: new
scale_t_bot_tsla  | 2025-05-20 20:59:10,014 - SCALE_T.decision_maker - INFO - Handling order update. Order status: pending_new, Order ID: 87c5e0a2-2ad3-4346-83e9-06eefecd9400
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Handling order update. Order status: pending_new, Order ID: 87c5e0a2-2ad3-4346-83e9-06eefecd9400
scale_t_bot_tsla  | 2025-05-20 20:59:10,015 - SCALE_T.decision_maker - INFO - Order pending
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Order pending
scale_t_bot_tsla  | 2025-05-20 20:59:10,015 - SCALE_T.decision_maker - INFO - Order status: PENDING. Status: pending_new
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Order status: PENDING. Status: pending_new
scale_t_bot_tsla  | 2025-05-20 20:59:10,016 - SCALE_T.decision_maker - INFO - Handling order update from redis
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Handling order update from redis
scale_t_bot_tsla  | DEBUG:SCALE_T.decision_maker:Handling order update. Current pending order is id=UUID('87c5e0a2-2ad3-4346-83e9-06eefecd9400') client_order_id='ed6e431b-f1d6-483d-8561-d8e9bea736f4' created_at=datetime.datetime(2025, 5, 20, 20, 59, 5, 55569, tzinfo=TzInfo(UTC)) updated_at=datetime.datetime(2025, 5, 20, 20, 59, 5, 57154, tzinfo=TzInfo(UTC)) submitted_at=datetime.datetime(2025, 5, 20, 20, 59, 5, 55569, 
tzinfo=TzInfo(UTC)) filled_at=None expired_at=None expires_at=datetime.datetime(2025, 5, 21, 0, 0, tzinfo=TzInfo(UTC)) canceled_at=None failed_at=None replaced_at=None replaced_by=None replaces=None asset_id=UUID('8ccae427-5dd0-45b3-b5fe-7ba5e422c766') symbol='TSLA' asset_class=<AssetClass.US_EQUITY: 'us_equity'> notional=None qty='1' filled_qty='0' filled_avg_price=None order_class=<OrderClass.SIMPLE: 'simple'> order_type=<OrderType.LIMIT: 'limit'> type=<OrderType.LIMIT: 'limit'> side=<OrderSide.BUY: 'buy'> time_in_force=<TimeInForce.DAY: 'day'> limit_price='344.33' stop_price=None status=<OrderStatus.PENDING_NEW: 'pending_new'> extended_hours=True legs=None trail_percent=None trail_price=None hwm=None position_intent=<PositionIntent.BUY_TO_OPEN: 'buy_to_open'> ratio_qty=None
scale_t_bot_tsla  | DEBUG:SCALE_T.decision_maker:Incoming order id=UUID('87c5e0a2-2ad3-4346-83e9-06eefecd9400') client_order_id='ed6e431b-f1d6-483d-8561-d8e9bea736f4' created_at=datetime.datetime(2025, 5, 20, 20, 59, 5, 55569, tzinfo=TzInfo(UTC)) updated_at=datetime.datetime(2025, 5, 20, 20, 59, 5, 63383, tzinfo=TzInfo(UTC)) submitted_at=datetime.datetime(2025, 5, 20, 20, 59, 5, 62110, tzinfo=TzInfo(UTC)) filled_at=None expired_at=None expires_at=None canceled_at=None failed_at=None replaced_at=None replaced_by=None replaces=None asset_id=UUID('8ccae427-5dd0-45b3-b5fe-7ba5e422c766') symbol='TSLA' asset_class=<AssetClass.US_EQUITY: 'us_equity'> notional=None qty='1' filled_qty='0' filled_avg_price=None order_class=<OrderClass.SIMPLE: 'simple'> order_type=<OrderType.LIMIT: 'limit'> type=None side=<OrderSide.BUY: 'buy'> time_in_force=<TimeInForce.DAY: 'day'> limit_price='344.33' stop_price=None status=<OrderStatus.NEW: 'new'> extended_hours=True legs=None trail_percent=None trail_price=None hwm=None position_intent=None ratio_qty=None        
scale_t_bot_tsla  | DEBUG:SCALE_T.decision_maker:At index 10 of type <class 'int'>
scale_t_bot_tsla  | 2025-05-20 20:59:10,017 - SCALE_T.decision_maker - INFO - Handling order update. Order status: new, Order ID: 87c5e0a2-2ad3-4346-83e9-06eefecd9400
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Handling order update. Order status: new, Order ID: 87c5e0a2-2ad3-4346-83e9-06eefecd9400
scale_t_bot_tsla  | 2025-05-20 20:59:10,018 - SCALE_T.decision_maker - INFO - Order pending
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Order pending
scale_t_bot_tsla  | 2025-05-20 20:59:10,018 - SCALE_T.decision_maker - INFO - Order status: PENDING. Status: new
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Order status: PENDING. Status: new
alpaca_broker     | DEBUG:SCALE_T.AlpacaBroker:Handling order update: event=<TradeEvent.FILL: 'fill'> execution_id=UUID('a5518d51-1d61-436b-a15c-de823b6b19e8') order={   'asset_class': <AssetClass.US_EQUITY: 'us_equity'>,
alpaca_broker     |     'asset_id': UUID('8ccae427-5dd0-45b3-b5fe-7ba5e422c766'),
firebase_client   | 2025-05-20 20:59:51 - FirebaseRedisSubscriber - WARNING - Received message on unknown channel:
alpaca_broker     |     'canceled_at': None,
alpaca_broker     |     'client_order_id': 'ed6e431b-f1d6-483d-8561-d8e9bea736f4',
alpaca_broker     |     'created_at': datetime.datetime(2025, 5, 20, 20, 59, 5, 55569, tzinfo=datetime.timezone.utc),
alpaca_broker     |     'expired_at': None,
alpaca_broker     |     'extended_hours': True,
scale_t_bot_tsla  | 2025-05-20 20:59:51,711 - SCALE_T.decision_maker - INFO - Trade update: event='fill' execution_id=None order={   'asset_class': <AssetClass.US_EQUITY: 'us_equity'>,
alpaca_broker     |     'failed_at': None,
scale_t_bot_tsla  |     'asset_id': UUID('8ccae427-5dd0-45b3-b5fe-7ba5e422c766'),
alpaca_broker     |     'filled_at': datetime.datetime(2025, 5, 20, 20, 59, 48, 102882, tzinfo=datetime.timezone.utc),
scale_t_bot_tsla  |     'canceled_at': None,
alpaca_broker     |     'filled_avg_price': '344.3',
scale_t_bot_tsla  |     'client_order_id': 'ed6e431b-f1d6-483d-8561-d8e9bea736f4',
alpaca_broker     |     'filled_qty': '1',
scale_t_bot_tsla  |     'created_at': datetime.datetime(2025, 5, 20, 20, 59, 5, 55569, tzinfo=TzInfo(UTC)),
alpaca_broker     |     'hwm': None,
scale_t_bot_tsla  |     'expired_at': None,
alpaca_broker     |     'id': UUID('87c5e0a2-2ad3-4346-83e9-06eefecd9400'),
scale_t_bot_tsla  |     'expires_at': None,
alpaca_broker     |     'legs': None,
scale_t_bot_tsla  |     'extended_hours': True,
alpaca_broker     |     'limit_price': '344.33',
scale_t_bot_tsla  |     'failed_at': None,
alpaca_broker     |     'notional': None,
scale_t_bot_tsla  |     'filled_at': datetime.datetime(2025, 5, 20, 20, 59, 48, 102882, tzinfo=TzInfo(UTC)),
alpaca_broker     |     'order_class': <OrderClass.SIMPLE: 'simple'>,
scale_t_bot_tsla  |     'filled_avg_price': '344.3',
alpaca_broker     |     'order_type': <OrderType.LIMIT: 'limit'>,
scale_t_bot_tsla  |     'filled_qty': '1',
alpaca_broker     |     'qty': '1',
scale_t_bot_tsla  |     'hwm': None,
alpaca_broker     |     'replaced_at': None,
scale_t_bot_tsla  |     'id': UUID('87c5e0a2-2ad3-4346-83e9-06eefecd9400'),
alpaca_broker     |     'replaced_by': None,
scale_t_bot_tsla  |     'legs': None,
alpaca_broker     |     'replaces': None,
scale_t_bot_tsla  |     'limit_price': '344.33',
alpaca_broker     |     'side': <OrderSide.BUY: 'buy'>,
scale_t_bot_tsla  |     'notional': None,
alpaca_broker     |     'status': <OrderStatus.FILLED: 'filled'>,
scale_t_bot_tsla  |     'order_class': <OrderClass.SIMPLE: 'simple'>,
alpaca_broker     |     'stop_price': None,
scale_t_bot_tsla  |     'order_type': <OrderType.LIMIT: 'limit'>,
alpaca_broker     |     'submitted_at': datetime.datetime(2025, 5, 20, 20, 59, 5, 62110, tzinfo=datetime.timezone.utc),
scale_t_bot_tsla  |     'position_intent': None,
alpaca_broker     |     'symbol': 'TSLA',
scale_t_bot_tsla  |     'qty': '1',
alpaca_broker     |     'time_in_force': <TimeInForce.DAY: 'day'>,
scale_t_bot_tsla  |     'ratio_qty': None,
alpaca_broker     |     'trail_percent': None,
scale_t_bot_tsla  |     'replaced_at': None,
alpaca_broker     |     'trail_price': None,
scale_t_bot_tsla  |     'replaced_by': None,
alpaca_broker     |     'type': <OrderType.LIMIT: 'limit'>,
scale_t_bot_tsla  |     'replaces': None,
alpaca_broker     |     'updated_at': datetime.datetime(2025, 5, 20, 20, 59, 48, 105518, tzinfo=datetime.timezone.utc)} timestamp=datetime.datetime(2025, 5, 20, 20, 59, 48, 102882, tzinfo=datetime.timezone.utc) 
position_qty=1.0 price=344.3 qty=1.0
scale_t_bot_tsla  |     'side': <OrderSide.BUY: 'buy'>,
alpaca_broker     | INFO:main.utils.redis.publisher:Published message to TICKER_UPDATES_TSLA
scale_t_bot_tsla  |     'status': <OrderStatus.FILLED: 'filled'>,
alpaca_broker     | DEBUG:SCALE_T.AlpacaBroker:Published to TICKER_UPDATES_TSLA: {'type': 'order', 'timestamp': '2025-05-20 20:59:48.102882+00:00', 'symbol': 'TSLA', 'order_data': {'event': <TradeEvent.FILL: 'fill'>, 'execution_id': 'a5518d51-1d61-436b-a15c-de823b6b19e8', 'order': {'id': '87c5e0a2-2ad3-4346-83e9-06eefecd9400', 'client_order_id': 'ed6e431b-f1d6-483d-8561-d8e9bea736f4', 'created_at': '2025-05-20 20:59:05.055569+00:00', 'updated_at': '2025-05-20 20:59:48.105518+00:00', 'submitted_at': '2025-05-20 20:59:05.062110+00:00', 'filled_at': '2025-05-20 20:59:48.102882+00:00', 'expired_at': None, 'canceled_at': None, 'failed_at': None, 'replaced_at': None, 'replaced_by': None, 'replaces': None, 'asset_id': '8ccae427-5dd0-45b3-b5fe-7ba5e422c766', 'symbol': 'TSLA', 'asset_class': 'us_equity', 'notional': None, 'qty': '1', 'filled_qty': '1', 'filled_avg_price': '344.3', 'order_class': 'simple', 'order_type': 'limit', 'side': 'buy', 'time_in_force': 'day', 'limit_price': '344.33', 'stop_price': None, 'status': 'filled', 'extended_hours': 
True, 'legs': None, 'trail_percent': None, 'trail_price': None, 'hwm': None, 'source': 'alpaca'}, 'timestamp': '2025-05-20 20:59:48.102882+00:00', 'position_qty': '1.0', 'price': '344.3', 'qty': '1.0'}}
scale_t_bot_tsla  |     'stop_price': None,
scale_t_bot_tsla  |     'submitted_at': datetime.datetime(2025, 5, 20, 20, 59, 5, 62110, tzinfo=TzInfo(UTC)),
scale_t_bot_tsla  |     'symbol': 'TSLA',
scale_t_bot_tsla  |     'time_in_force': <TimeInForce.DAY: 'day'>,
scale_t_bot_tsla  |     'trail_percent': None,
scale_t_bot_tsla  |     'trail_price': None,
scale_t_bot_tsla  |     'type': None,
scale_t_bot_tsla  |     'updated_at': datetime.datetime(2025, 5, 20, 20, 59, 48, 105518, tzinfo=TzInfo(UTC))} timestamp=datetime.datetime(2025, 5, 20, 20, 59, 48, 102882, tzinfo=datetime.timezone.utc) position_qty=None price=None qty=None
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Trade update: event='fill' execution_id=None order={   'asset_class': <AssetClass.US_EQUITY: 'us_equity'>,
scale_t_bot_tsla  |     'asset_id': UUID('8ccae427-5dd0-45b3-b5fe-7ba5e422c766'),
scale_t_bot_tsla  |     'canceled_at': None,
scale_t_bot_tsla  |     'client_order_id': 'ed6e431b-f1d6-483d-8561-d8e9bea736f4',
scale_t_bot_tsla  |     'created_at': datetime.datetime(2025, 5, 20, 20, 59, 5, 55569, tzinfo=TzInfo(UTC)),
scale_t_bot_tsla  |     'expired_at': None,
scale_t_bot_tsla  |     'expires_at': None,
scale_t_bot_tsla  |     'extended_hours': True,
scale_t_bot_tsla  |     'failed_at': None,
scale_t_bot_tsla  |     'filled_at': datetime.datetime(2025, 5, 20, 20, 59, 48, 102882, tzinfo=TzInfo(UTC)),
scale_t_bot_tsla  |     'filled_avg_price': '344.3',
scale_t_bot_tsla  |     'filled_qty': '1',
scale_t_bot_tsla  |     'hwm': None,
scale_t_bot_tsla  |     'id': UUID('87c5e0a2-2ad3-4346-83e9-06eefecd9400'),
scale_t_bot_tsla  |     'legs': None,
scale_t_bot_tsla  |     'limit_price': '344.33',
scale_t_bot_tsla  |     'notional': None,
scale_t_bot_tsla  |     'order_class': <OrderClass.SIMPLE: 'simple'>,
scale_t_bot_tsla  |     'order_type': <OrderType.LIMIT: 'limit'>,
scale_t_bot_tsla  |     'position_intent': None,
scale_t_bot_tsla  |     'qty': '1',
scale_t_bot_tsla  |     'ratio_qty': None,
scale_t_bot_tsla  |     'replaced_at': None,
scale_t_bot_tsla  |     'replaced_by': None,
scale_t_bot_tsla  |     'replaces': None,
scale_t_bot_tsla  |     'side': <OrderSide.BUY: 'buy'>,
scale_t_bot_tsla  |     'status': <OrderStatus.FILLED: 'filled'>,
scale_t_bot_tsla  |     'stop_price': None,
scale_t_bot_tsla  |     'submitted_at': datetime.datetime(2025, 5, 20, 20, 59, 5, 62110, tzinfo=TzInfo(UTC)),
scale_t_bot_tsla  |     'symbol': 'TSLA',
scale_t_bot_tsla  |     'time_in_force': <TimeInForce.DAY: 'day'>,
scale_t_bot_tsla  |     'trail_percent': None,
scale_t_bot_tsla  |     'trail_price': None,
scale_t_bot_tsla  |     'type': None,
scale_t_bot_tsla  |     'updated_at': datetime.datetime(2025, 5, 20, 20, 59, 48, 105518, tzinfo=TzInfo(UTC))} timestamp=datetime.datetime(2025, 5, 20, 20, 59, 48, 102882, tzinfo=datetime.timezone.utc) position_qty=None price=None qty=None
scale_t_bot_tsla  | 2025-05-20 20:59:51,712 - SCALE_T.decision_maker - INFO - Trade update event: fill
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Trade update event: fill
scale_t_bot_tsla  | 2025-05-20 20:59:51,712 - SCALE_T.decision_maker - INFO - Handling order update from redis
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Handling order update from redis
scale_t_bot_tsla  | DEBUG:SCALE_T.decision_maker:Handling order update. Current pending order is id=UUID('87c5e0a2-2ad3-4346-83e9-06eefecd9400') client_order_id='ed6e431b-f1d6-483d-8561-d8e9bea736f4' created_at=datetime.datetime(2025, 5, 20, 20, 59, 5, 55569, tzinfo=TzInfo(UTC)) updated_at=datetime.datetime(2025, 5, 20, 20, 59, 5, 57154, tzinfo=TzInfo(UTC)) submitted_at=datetime.datetime(2025, 5, 20, 20, 59, 5, 55569, 
tzinfo=TzInfo(UTC)) filled_at=None expired_at=None expires_at=datetime.datetime(2025, 5, 21, 0, 0, tzinfo=TzInfo(UTC)) canceled_at=None failed_at=None replaced_at=None replaced_by=None replaces=None asset_id=UUID('8ccae427-5dd0-45b3-b5fe-7ba5e422c766') symbol='TSLA' asset_class=<AssetClass.US_EQUITY: 'us_equity'> notional=None qty='1' filled_qty='0' filled_avg_price=None order_class=<OrderClass.SIMPLE: 'simple'> order_type=<OrderType.LIMIT: 'limit'> type=<OrderType.LIMIT: 'limit'> side=<OrderSide.BUY: 'buy'> time_in_force=<TimeInForce.DAY: 'day'> limit_price='344.33' stop_price=None status=<OrderStatus.PENDING_NEW: 'pending_new'> extended_hours=True legs=None trail_percent=None trail_price=None hwm=None position_intent=<PositionIntent.BUY_TO_OPEN: 'buy_to_open'> ratio_qty=None
scale_t_bot_tsla  | DEBUG:SCALE_T.decision_maker:Incoming order id=UUID('87c5e0a2-2ad3-4346-83e9-06eefecd9400') client_order_id='ed6e431b-f1d6-483d-8561-d8e9bea736f4' created_at=datetime.datetime(2025, 5, 20, 20, 59, 5, 55569, tzinfo=TzInfo(UTC)) updated_at=datetime.datetime(2025, 5, 20, 20, 59, 48, 105518, tzinfo=TzInfo(UTC)) submitted_at=datetime.datetime(2025, 5, 20, 20, 59, 5, 62110, tzinfo=TzInfo(UTC)) filled_at=datetime.datetime(2025, 5, 20, 20, 59, 48, 102882, tzinfo=TzInfo(UTC)) expired_at=None expires_at=None canceled_at=None failed_at=None replaced_at=None replaced_by=None replaces=None asset_id=UUID('8ccae427-5dd0-45b3-b5fe-7ba5e422c766') symbol='TSLA' asset_class=<AssetClass.US_EQUITY: 'us_equity'> notional=None qty='1' filled_qty='1' filled_avg_price='344.3' order_class=<OrderClass.SIMPLE: 'simple'> order_type=<OrderType.LIMIT: 'limit'> type=None side=<OrderSide.BUY: 'buy'> time_in_force=<TimeInForce.DAY: 'day'> limit_price='344.33' stop_price=None status=<OrderStatus.FILLED: 'filled'> extended_hours=True legs=None trail_percent=None trail_price=None hwm=None position_intent=None ratio_qty=None
scale_t_bot_tsla  | DEBUG:SCALE_T.decision_maker:At index 10 of type <class 'int'>
scale_t_bot_tsla  | 2025-05-20 20:59:51,714 - SCALE_T.decision_maker - INFO - Handling order update. Order status: filled, Order ID: 87c5e0a2-2ad3-4346-83e9-06eefecd9400
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Handling order update. Order status: filled, Order ID: 87c5e0a2-2ad3-4346-83e9-06eefecd9400
scale_t_bot_tsla  | 2025-05-20 20:59:51,714 - SCALE_T.decision_maker - INFO - Order filled
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Order filled
scale_t_bot_tsla  | 2025-05-20 20:59:51,714 - SCALE_T.decision_maker - INFO - Order status: FILLED. Filled quantity: 1.0, Filled average price: 344.3, Order side: buy
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Order status: FILLED. Filled quantity: 1.0, Filled average price: 344.3, Order side: buy
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Distributing 1.0 shares to rows above 10
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Assigning 0.13 shares to index 0, filled_qty: 1.0
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After assignment, filled_qty: 0.87
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Before unrealized profit update, existing: 0.0
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After unrealized profit update, new: 2.52
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Assigning 0.14 shares to index 1, filled_qty: 0.87
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After assignment, filled_qty: 0.73
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Before unrealized profit update, existing: 0.0
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After unrealized profit update, new: 2.46
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Assigning 0.14 shares to index 2, filled_qty: 0.73
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After assignment, filled_qty: 0.59
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Before unrealized profit update, existing: 0.0
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After unrealized profit update, new: 2.21
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Assigning 0.14 shares to index 3, filled_qty: 0.59
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After assignment, filled_qty: 0.44999999999999996
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Before unrealized profit update, existing: 0.0
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After unrealized profit update, new: 1.96
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Assigning 0.14 shares to index 4, filled_qty: 0.44999999999999996
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After assignment, filled_qty: 0.30999999999999994
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Before unrealized profit update, existing: 0.0
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After unrealized profit update, new: 1.71
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Assigning 0.14 shares to index 5, filled_qty: 0.30999999999999994
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After assignment, filled_qty: 0.16999999999999993
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Before unrealized profit update, existing: 0.0
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After unrealized profit update, new: 1.46
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Assigning 0.14 shares to index 6, filled_qty: 0.16999999999999993
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After assignment, filled_qty: 0.029999999999999916
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Before unrealized profit update, existing: 0.0
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After unrealized profit update, new: 1.21
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Assigning 0.029999999999999916 shares to index 7, filled_qty: 0.029999999999999916
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After assignment, filled_qty: 0.0
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:Before unrealized profit update, existing: 0.0
scale_t_bot_tsla  | DEBUG:SCALE_T.csv_service:After unrealized profit update, new: 0.21
scale_t_bot_tsla  | 2025-05-20 20:59:51,733 - SCALE_T.decision_maker - INFO - Order filled and handled successfully. Checking share count.
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Order filled and handled successfully. Checking share count.
scale_t_bot_tsla  | 2025-05-20 20:59:51,813 - SCALE_T.decision_maker - INFO - Shares count verified: Alpaca (1.0) vs CSV (1.0)
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Shares count verified: Alpaca (1.0) vs CSV (1.0)
performance       | INFO:main.performance.daily_profit_calc:Processing profit message: {'data': {'realized': 0.0, 'unrealized': 13.742299999999991, 'converted': 0.0, 'total': 13.742299999999991, 'symbol': 'TSLA''timestamp': '2025-05-20T20:59:51.814041+00:00'}                                                              e_t'}
scale_t_bot_tsla  | INFO:SCALE_T.decision_maker:Profit report published: {'realized': 0.0, 'unrealized': 13.742299999999991, 'converted': 0.0, 'total': 13.742299999999991, 'symbol': 'TSLA', 'timestamp': '2025-05-20T20:59zed': 0.0, 'unrealized': 13.742299999999991, 'converted': 0.0, 'total': 13.742299999999991, 'symbol'::51.814041+00:00'}
performance       | INFO:main.utils.redis.connection:Connected to Redis at redis:6379/0                       2299999999991, 'converted': 0.0, 'total': 13.742299999999991, 'symbol': 'TSLA', 'timestamp': '2025-05
firebase_client   | 2025-05-20 20:59:51 - FirebaseRedisSubscriber - WARNING - Received message on unknown channel:
performance       | INFO:main.utils.redis.publisher:Published message to TICKER_PERFORMANCE_TSLA              nel: 
firebase_client   | 2025-05-20 20:59:51 - FirebaseRedisSubscriber - WARNING - Received message on unknown channel:                                                                                                          nel:
performance       | INFO:main.performance.daily_profit_calc:Published performance data for TSLA to Redis      
performance       | INFO:main.utils.redis.publisher:Published message to TICKER_PERFORMANCE_AGGREGATE
performance       | INFO:main.performance.daily_profit_calc:Published performance data for aggregate to Redis 

Our goal is to store the prices, orders and performance:

This is our redis subscriber:
main\firebase_client\src\redis_subscriber.py

This is our firebase client:
main\firebase_client\src\firebase_client.py

this is the main file for our firebase client:
main\firebase_client\src\main.py


this is the redis service:
main\utils\redis\constants.py

And how we use it main\utils\redis\README.md

What examply is going on? let's brainstorm why I am unable to now get the stock prices and other additional data, also let's create a log file that will store all of the logs in our firebase container to better debug the issue