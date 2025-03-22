import os
import csv
import json
import time
from main.bots.SCALE_T.common.constants import (
    get_ticker_filepath,
    TEMPLATE_CSV,
    METADATA_FILE,
    PAPER_TRADING,
    LIVE_TRADING
)

def _load_metadata():
    """Loads the metadata JSON file."""
    metadata_path = os.path.join('data', 'SCALE_T', 'templates', METADATA_FILE)
    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Metadata file not found: {metadata_path}")
        return {}  # Return an empty dictionary if file not found

def _get_required_columns():
    """Extracts and returns a list of required column names from the metadata."""
    metadata = _load_metadata()
    required_columns = []
    if metadata and 'versions' in metadata and metadata['versions']:
        # Assuming we use the first version in the list
        columns = metadata['versions'][0]['columns']
        for column in columns:
            if column['config']['required']:
                required_columns.append(column['name'])
    return required_columns

def create_row(index, buy_price):
    sell_price = round(buy_price * 1.005, 2)
    # target_shares = int(300 / buy_price)
    target_shares = 1
    return {
        'index': str(index),
        'buy_price': str(buy_price),
        'sell_price': str(sell_price),
        'target_shares': str(target_shares),
        'held_shares': '0',
        'pending_order_id': 'None',
        'profit': '0.0',
        'unrealized_profit': '0.0',
        'last_action': str(int(time.time())),
        'spc': 'N'
    }

if __name__ == '__main__':
    ticker = input("Enter the ticker symbol: ").upper()
    initial_buy_price = float(input("Enter the initial buy price: "))
    trading_type = 'paper'
    num_rows = 50
    metadata = _load_metadata()
    required_columns = _get_required_columns()
    
    csv_data = []
    first_row = create_row(0, initial_buy_price)
    csv_data.append(first_row)

    for i in range(1, num_rows):
        prev_row = csv_data[i - 1]
        # Calculate a decreasing buy price (0.5% decrease from previous row's buy price)
        next_buy_price = round(float(prev_row['buy_price']) * 0.995, 2)
        next_row = create_row(i, next_buy_price)
        csv_data.append(next_row)

    filepath = get_ticker_filepath(ticker, trading_type)
    # added this to create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=required_columns)
        writer.writeheader()
        writer.writerows(csv_data)

    print(f"CSV file created at: {filepath}")
