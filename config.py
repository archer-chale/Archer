import json

def load_config():
    with open('configs/config.json') as config_file:
        return json.load(config_file)
