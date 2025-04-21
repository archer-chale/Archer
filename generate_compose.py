import yaml

with open("configs/tickers.txt") as f:
    tickers = [line.strip() for line in f]



services = {}
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
    "services": services
}

with open("docker-compose.generated.yml", "w") as f:
    yaml.dump(compose, f)
