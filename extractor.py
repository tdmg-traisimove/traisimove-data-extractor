from typing import List

from pymongo import database


def get_users_ids(
    db: database.Database,
    studies_names: List[str],
) -> None:

    uuids_documents = db.Stage_uuids.find(
        {
            "user_email": {"$regex": f"^nrelop_({"|".join(studies_names)})_default_.*"},
        },
        sort=[("$natural", -1)],  # we want the most recent user first
    )

    for uuids_document in uuids_documents:
        print(uuids_document)


def extract(db: database.Database, studies_names: List[str]) -> None:
    get_users_ids(db, studies_names)
