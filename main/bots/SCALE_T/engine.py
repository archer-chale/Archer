"""
Engine starter for SCALE_T bot.

This module contains the function to start the SCALE_T trading bot engine.
In a classless implementation, this module focuses on the initial setup and orchestration.
"""

import argparse

from .csv_utils.csv_service import CSVService
from .brokerages.alpaca_interface import AlpacaInterface
from .trading.decision_maker import DecisionMaker
from .common.logging_config import LoggerConfig
from .common.constants import TradingType, DataPathType, get_data_path
###################logging.basicConfig(level=logging.INFO)
#.env log levels

def run_engine(ticker: str, trading_type: TradingType):
    """
    Starts the SCALE_T trading bot engine.

    Args:
        ticker (str): The stock ticker symbol to trade.
        trading_type (str): The trading type ('paper' or 'live').
    """
    try :
        # TODO: container name should be coming from run_bot config, DOCKERFILE ??
        container_name = '_'.join(['ST', ticker ,trading_type.value])
        log_base_path = get_data_path(trading_type=trading_type, data_path_type=DataPathType.LOGS)
        logger_config: LoggerConfig = LoggerConfig(bot_name=container_name, log_base_path=log_base_path)
        logger = logger_config.get_logger("engine")
        logger.info(f"Starting engine with ticker: {ticker} and trading type: {trading_type}")

        csv_service = CSVService(ticker=ticker, trading_type=trading_type, logger_config=logger_config)
        alpaca_interface = AlpacaInterface(trading_type=trading_type, ticker=ticker, logger_config=logger_config)
        decision_maker = DecisionMaker(csv_service=csv_service, alpaca_interface=alpaca_interface, logger_config=logger_config)
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
