import json

with open("credentials.json") as f:
    config = json.load(f)


OPENAI_API_KEY = config["OPENAI_API_KEY"]
