import yaml
import os, sys
from main.bots.SCALE_T.brokerages.alpaca_interface import AlpacaInterface
from main.bots.SCALE_T.common.constants import TradingType

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
if not os.path.exists("./data/SCALE_T/ticker_data/paper"):
    os.makedirs("./data/SCALE_T/ticker_data/paper")
    print("data folder created.")

alpaca_interface = AlpacaInterface(TradingType.PAPER)
for ticker in tickers:
    if not os.path.exists(f"./data/SCALE_T/ticker_data/paper/{ticker.upper()}.csv"):
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
}

# Add bot services
for ticker in tickers:
    services[f"scale_t_bot_{ticker.lower()}"] = {
        "build": {
            "context": ".",
            "dockerfile": f"main/bots/SCALE_T/Dockerfile",
        },
        "command": f"{ticker.upper()} paper",
        "container_name": f"scale_t_bot_{ticker.lower()}",
        "volumes": [
            f"./data/SCALE_T/ticker_data/paper/{ticker.upper()}.csv:/app/data/ticker_data/paper/{ticker.upper()}.csv",
        ],
        "restart": "no",
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
