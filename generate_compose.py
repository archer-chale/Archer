import yaml

with open("configs/tickers.txt") as f:
    tickers = [line.strip() for line in f]

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
    }
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
