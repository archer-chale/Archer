"""
Engine starter for SCALE_T bot.

This module contains the function to start the SCALE_T trading bot engine.
In a classless implementation, this module focuses on the initial setup and orchestration.
"""

import argparse

from main.bots.SCALE_T.csv_utils.csv_service import CSVService
from main.bots.SCALE_T.brokerages.alpaca_interface import AlpacaInterface
from main.bots.SCALE_T.trading.decision_maker import DecisionMaker
from main.bots.SCALE_T.common.logging_config import get_logger
from main.bots.SCALE_T.common.constants import TradingType
###################logging.basicConfig(level=logging.INFO)
#.env log levels

def run_engine(ticker: str, trading_type: str):
    """
    Starts the SCALE_T trading bot engine.

    Args:
        ticker (str): The stock ticker symbol to trade.
        trading_type (str): The trading type ('paper' or 'live').
    """
    logger = get_logger("engine")
    logger.info(f"Starting engine with ticker: {ticker} and trading type: {trading_type}")

    try :
        csv_service = CSVService(ticker=ticker, trading_type=trading_type)
        alpaca_interface = AlpacaInterface(trading_type=trading_type, ticker=ticker)
        decision_maker = DecisionMaker(csv_service=csv_service, alpaca_interface=alpaca_interface)
        decision_maker.launch_action_producer_threads()
        logger.info("Engine Started")
        decision_maker.consume_actions()
    except Exception as e:
        logger.error(f"Engine failure on error {e}")
        raise RuntimeError(e)


if __name__ == "__main__":
    # Example usage (for testing/running engine directly)
    parser = argparse.ArgumentParser(description="Run the SCALE-T trading bot engine.")
    parser.add_argument("ticker", type=str, help="The stock ticker symbol to trade (e.g., AAPL).")
    parser.add_argument("trading_type", type=TradingType, choices=list(TradingType), help="Trading type ('paper' or 'live').")

    args = parser.parse_args()

    run_engine(ticker=args.ticker, trading_type=args.trading_type)
