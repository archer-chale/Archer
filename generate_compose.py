import yaml
import os, sys
from main.bots.SCALE_T.brokerages.alpaca_interface import AlpacaInterface
from main.bots.SCALE_T.common.constants import TradingType, TRADING_TYPE_TO_PATH
import argparse

parser = argparse.ArgumentParser(description="Generate docker-compose file for SCALE_T bot.")
parser.add_argument(
    "--trading_type",
    type=TradingType,
    choices=list(TradingType),
    default=TradingType.PAPER,
    help="Trading type: 'paper' or 'live'. Default is 'paper'.",
)
args = parser.parse_args()
trading_type = args.trading_type

from main.bots.SCALE_T.csv_utils.csv_tool import CSVWorker
# Ensure configs folder exists
# .env existence 
if not os.path.exists("configs"):
    os.makedirs("configs")
    print("configs folder created.")
if not os.path.exists("configs/.env"):
    print("configs/.env file does not exist.")
    print("Please add your .env file to the configs folder.")
    sys.exit(1) 
# tickers.txt existence and save as list

# Ensure data folder exists
tickers_list_path = "configs/tickers.txt"
if not os.path.exists(tickers_list_path):
    print(f"{tickers_list_path} file does not exist.")
    print("Please add your tickers.txt file to the configs folder.")
    sys.exit(1)
with open("configs/tickers.txt") as f:
    tickers = [line.strip() for line in f]

# Ensure data folder for tickers exists
tickers_data_path = TRADING_TYPE_TO_PATH[trading_type]
if not os.path.exists(tickers_data_path):
    os.makedirs(tickers_data_path)
    print("data folder for tickers created.")
    
# Ensure data folder for performance exists
if not os.path.exists("./data/performance"):
    os.makedirs("./data/performance")
    print("data folder for performance created.")

print("All data files exist. Proceeding to generate docker-compose file.")

services = {
    "redis": {
        "image": "redis:latest", # Using latest as per docker-compose.yml
        "container_name": "redis",
        "ports": ["6379:6379"],
        "volumes": ["redis-data:/data"], # Added volume from docker-compose.yml
        "command": "redis-server --appendonly yes", # Added command from docker-compose.yml
        "restart": "unless-stopped",
        "logging": {
            "driver": "json-file",
            "options": {
                "max-size": "10m",
                "max-file": "3"
            }
        }
    },
    "alpaca_broker": {
        "build": {
            "context": ".",
            "dockerfile": "main/alpaca_broker/Dockerfile",
        },
        "container_name": "alpaca_broker",
        # "env_file": ['configs/.env'], # Restore env_file
        "restart": "no",
        "depends_on": ["redis"],
        "env_file": "configs/.env",
        "logging": {
            "driver": "json-file",
            "options": {
                "max-size": "10m",
                "max-file": "3"
            }
        },
    },
    "performance": {
        "build": {
            "context": ".",
            "dockerfile": "main/performance/Dockerfile",
        },
        "container_name": "performance",
        "volumes": [
            "./data/performance:/app/data/performance",
        ],
        "depends_on": ["redis"],
        "restart": "no",
        "logging": {
            "driver": "json-file",
            "options": {
                "max-size": "10m",
                "max-file": "3"
            }
        },
    },
    "firebase_client": {
        "build": {
            "context": ".",
            "dockerfile": "main/firebase_client/Dockerfile",
        },
        "container_name": "firebase_client",
        "restart": "no",
        "depends_on": ["alpaca_broker"],
        "logging": {
            "driver": "json-file",
            "options": {
                "max-size": "10m",
                "max-file": "3"
            }
        },
    },
}


alpaca_interface = AlpacaInterface(trading_type=trading_type)
# Add bot services
for ticker in tickers:
    # Create csv
    if not os.path.exists(os.path.join(tickers_data_path,f"{ticker.upper()}.csv")):
        if trading_type == TradingType.LIVE:
            print(f"For live trading, we require already existing data files.")
            print(f"Data file for {ticker} does not exist.")
            print(f"Please add your data file to the data folder.")
            sys.exit(1)
        print(f"Data file for {ticker} does not exist.")
        print(f"Trying to create a new one.")
        # Create a new file with the ticker name`1`
        worker = CSVWorker(ticker.upper(), TradingType.PAPER)
        # Create the answers
        alpaca_interface.ticker = ticker.upper()
        answers = {
            "total_cash": 10000,
            "risk_type": 2,
            "percentage_diff": 0.005,
            "starting_buy_price": round(alpaca_interface.get_current_price()*1.07,2),
            "distribution_style": "linear",
        }
        # Create the csv file
        worker.create_csv(answers)
        print(f"Created new data file for {ticker}.")

    services[f"scale_t_bot_{ticker.lower()}"] = {
        "build": {
            "context": ".",
            "dockerfile": f"main/bots/SCALE_T/Dockerfile",
        },
        "command": f"{ticker.upper()} {trading_type.value}",
        "container_name": f"scale_t_bot_{ticker.lower()}",
        "volumes": [
            f"./data/SCALE_T/ticker_data/{trading_type.value}/{ticker.upper()}.csv:/app/data/ticker_data/{trading_type.value}/{ticker.upper()}.csv",
        ],
        "restart": "no",
        "depends_on": ["alpaca_broker", "firebase_client"],
        "logging": {
            "driver": "json-file",
            "options": {
                "max-size": "10m",
                "max-file": "3"
            }
        },
    }

compose = {
    "services": services,
    "volumes": { # Added volumes section from docker-compose.yml
        "redis-data": None
    }
}

with open("docker-compose.generated.yml", "w") as f:
    yaml.dump(compose, f)
