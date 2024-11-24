import csv
import datetime
from typing import Dict, List, TypedDict

import bson
from pymongo import cursor, database


class UuidsDocument(TypedDict):
    _id: bson.ObjectId
    user_email: str
    uuid: bson.Binary
    update_ts: datetime.datetime


class ProfileDocument(TypedDict):
    _id: bson.ObjectId
    user_id: bson.Binary
    mode: object
    mpg_array: List[int]
    purpose: object
    source: str
    update_ts: datetime.datetime
    client_app_version: str
    client_os_version: str
    curr_platform: str
    manufacturer: str
    phone_lang: str
    pipeline_range: Dict[str, float]


class User(TypedDict):
    user_id: bson.Binary
    token: str
    client_app_version: str
    client_os_version: str
    curr_platform: str
    manufacturer: str
    phone_lang: str


def get_users(
    db: database.Database,
    studies_names: List[str],
) -> List[User]:

    uuids_documents: cursor.Cursor[UuidsDocument] = db.Stage_uuids.find(
        {
            "user_email": {"$regex": f"^nrelop_({"|".join(studies_names)})_default_.*"},
        },
    )

    uuids_to_token = {
        uuids_document["uuid"]: uuids_document["user_email"]
        for uuids_document in uuids_documents
    }

    profile_documents: cursor.Cursor[ProfileDocument] = db.Stage_Profiles.find(
        {
            "user_id": {"$in": list(uuids_to_token.keys())},
        },
        sort=[("$natural", -1)],  # we want the most recent profile first
    )

    users: List[User] = []

    for profile_document in profile_documents:
        user_id = profile_document["user_id"]
        token = uuids_to_token[user_id]
        user: User = {
            "user_id": profile_document["user_id"],
            "token": token,
            "client_app_version": profile_document["client_app_version"],
            "client_os_version": profile_document["client_os_version"],
            "curr_platform": profile_document["curr_platform"],
            "manufacturer": profile_document["manufacturer"],
            "phone_lang": profile_document["phone_lang"],
        }
        users.append(user)

    return users


headers_users = [
    "user_uuid",
    "token",
    "curr_platform",
    "client_app_version",
    "client_os_version",
    "manufacturer",
    "phone_lang",
]


def save_users(users: List[User]) -> None:
    with open("traisi_users.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(headers_users)
        for user in users:
            writer.writerow(
                [
                    user["user_id"].hex(),
                    user["token"],
                    user["curr_platform"],
                    user["client_app_version"],
                    user["client_os_version"],
                    user["manufacturer"],
                    user["phone_lang"],
                ]
            )
