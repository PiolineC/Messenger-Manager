import json
from messenger_manager import MessengerManager

with open("config.json", "r") as f:
    config = json.load(f)
            
name = config["name"]
password = config["password"]
client = MessengerManager(name, password, max_tries=1)
client.listen()