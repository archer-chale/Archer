"""
CSV Worker module for handling CSV processing tasks in the SCALE_T bot.

This module contains the CSVWorker class which provides functionality for
processing and manipulating CSV data according to the SCALE_T strategy.
"""

from typing import Dict, List, Optional, Union
from .csv_core import CSVCore


class CSVWorker(CSVCore):
    def __init__(self, ticker: str, trading_type: str, custom_id: Optional[str] = None, file_path: Optional[str] = None):
        super().__init__(ticker, trading_type, custom_id, file_path)
        


if __name__ == "__main__":
    # Example usage of the CSVWorker class
    import argparse
    from main.bots.SCALE_T.common.constants import get_ticker_filepath, PAPER_TRADING, LIVE_TRADING
    
    parser = argparse.ArgumentParser(description="CSV Worker for SCALE_T bot")
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker symbol (e.g., 'AAPL')")
    parser.add_argument("--trading-type", type=str, choices=[PAPER_TRADING, LIVE_TRADING], 
                        default=PAPER_TRADING, help="Trading type (paper or live)")
    parser.add_argument("--custom-id", type=str, help="Optional custom identifier for the CSV file")
    args = parser.parse_args()
    
    # Generate file path using the constants utility function
    csv_path = get_ticker_filepath(args.ticker, args.trading_type, args.custom_id)
    print(f"CSV path: {csv_path}")
    
    # Initialize and use CSVWorker
    worker = CSVWorker(args.ticker, args.trading_type, args.custom_id, csv_path)
    
    try:
        data = worker.load_csv()
        print(f"Loaded CSV for {args.ticker} with {len(data)} rows.")
        if data:
            print(f"Columns: {', '.join(data[0].keys())}")
    except Exception as e:
        print(f"Error loading CSV: {str(e)}")
        print("Creating a new CSV file...")
        worker.data = []  # Initialize empty data
    
    # Interactive loop
    running = True
    data_modified = False
    
    def print_menu():
        print("\n=== CSV Worker Menu ===")
        print("q. Save and quit")
        print("x. Quit without saving")
        
    while running:
        print_menu()
        choice = input("\nEnter your choice: ").lower()
        
        if choice == 'q':
            # Save and quit
            if data_modified:
                try:
                    worker.save_csv()
                    print(f"Data saved to {csv_path}")
                except Exception as e:
                    print(f"Error saving CSV: {str(e)}")
            else:
                print("No changes to save.")
            running = False
            
        elif choice == 'x':
            # Quit without saving
            if data_modified:
                confirm = input("You have unsaved changes. Are you sure you want to quit without saving? (y/n): ").lower()
                if confirm == 'y':
                    running = False
                    print("Exiting without saving changes.")
            else:
                running = False
                print("Exiting.")
                
        else:
            print("Invalid choice. Please try again.")
