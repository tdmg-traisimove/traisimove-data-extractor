import json
import sys
from typing import List, TypedDict

from pymongo import MongoClient

from extractor import extract
from session import create_session_refresher


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
    session = client.start_session()
    session_id = session.session_id
    db = client.Stage_database
    refresh_session_if_needed = create_session_refresher(db, session_id)

    extract(
        db, config["studies_names"], config["ignored_tokens"], refresh_session_if_needed
    )


if __name__ == "__main__":
    main()
