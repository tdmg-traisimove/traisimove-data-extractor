import json
import sys
from typing import List, TypedDict

from pymongo import MongoClient

from extractor import extract


class Config(TypedDict):
    db_url: str
    studies_names: List[str]
    ignored_tokens: List[str]


def main():
    if len(sys.argv) > 1:
        config_filename = sys.argv[1]
        with open(config_filename, "r") as config_file:
            config: Config = json.load(config_file)
    else:
        print("Usage: python main.py config.json")
        exit()

    client = MongoClient(config["db_url"])
    db = client.Stage_database

    extract(db, config["studies_names"], config["ignored_tokens"])


if __name__ == "__main__":
    main()
