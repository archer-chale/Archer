from main.bots.SCALE_T import ALPACA_BROKERAGE

def start_bot(ticker_symbol, brokerage_type=ALPACA_BROKERAGE, trading_type):
    """
    Starts the Smart Capital Allocation and Liquidity Engine for a specific ticker.
    """
    print(f"Processing ticker: {ticker_symbol}")
    # 1. Check ticker symbol has valid data locally
    # 2. Check brokerage validity
    # 2. Test Trading type validity
    # 3. Test keys existence and validity
    # - - Check ticker symbol on brokerage as well
    # 4. Check shares/orders match local data and brokerage data
    # 5. Start the bot process(Hopefully websocket)
    return f"Successfully  {ticker_symbol}"


# Will be uncommented when actuallying needed
# if __name__ == "__main__":
#     ticker = "AAPL"
#     trading_type = "day"  # Example trading type
#     result = start_bot(ticker, trading_type)
#     print(result)
