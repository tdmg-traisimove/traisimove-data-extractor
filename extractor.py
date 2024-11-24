from typing import List
from extractor_users import get_users, save_users


def extract(db: database.Database, studies_names: List[str]) -> None:
    users = get_users(db, studies_names)
    save_users(users)

