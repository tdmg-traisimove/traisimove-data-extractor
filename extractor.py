import csv
import json
from typing import Callable, List

import bson
from pymongo import database

from extractor_surveys_answers import extract_surveys_answers
from extractor_users import get_users, save_users

headers = [
    "user_uuid",
    "trip_id",
    "section_id",
    "start_fmt_time",
    "end_fmt_time",
    "duration",
    "start_fmt_time_section",
    "end_fmt_time_section",
    "duration_section",
    "start_loc_lon",
    "start_loc_lat",
    "end_loc_lon",
    "end_loc_lat",
    "distance",
    "start_loc_lon_section",
    "start_loc_lat_section",
    "end_loc_lon_section",
    "end_loc_lat_section",
    "distance_section",
    "predicted_modes",
    "manual_mode",
    "manual_purpose",
]

headers_traces = [
    "user_uuid",
    "trip_id",
    "section_id",
    "fmt_time",
    "latitude",
    "longitude",
    "ts",
    "altitude",
    "distance",
    "speed",
    "heading",
    "mode",
]

headers_users = [
    "user_uuid",
    "project_id",
    "email",
    "creation_ts",
    "curr_platform",
    "client_app_version",
    "phone_lang",
    "client_os_version",
    "manufacturer",
]


def find_manual_mode_label(db: database.Database, trip: dict) -> str:
    manual_mode = db.Stage_timeseries.find(
        {
            "data.start_ts": trip["data"]["start_ts"],
            "metadata.key": "manual/mode_confirm",
        },
        no_cursor_timeout=True,
    )
    manual_mode_label = ""
    for m in manual_mode:
        manual_mode_label = m["data"]["label"]
    return manual_mode_label


def find_manual_purpose_label(db: database.Database, trip: dict) -> str:
    manual_purpose = db.Stage_timeseries.find(
        {
            "data.start_ts": trip["data"]["start_ts"],
            "metadata.key": "manual/purpose_confirm",
        },
        no_cursor_timeout=True,
    )
    manual_purpose_label = ""
    for m in manual_purpose:
        manual_purpose_label = m["data"]["label"]
    return manual_purpose_label


def find_mode_predicted_label(
    db: database.Database, user_id: bson.Binary, trip: dict, section: dict
) -> str:
    mode_predicted = db.Stage_analysis_timeseries.find(
        {
            "user_id": user_id,
            "metadata.key": "inference/prediction",
            "data.trip_id": trip["_id"],
            "data.section_id": section["_id"],
        },
        no_cursor_timeout=True,
    )
    mode_predicted_label = ""
    for m in mode_predicted:
        for key in m["data"]["predicted_mode_map"].keys():
            mode_predicted_label = key
    return mode_predicted_label


def extract_sections(
    db: database.Database,
    user_id: bson.Binary,
    trip: dict,
    section: dict,
    writer,
    manual_mode_label: str,
    manual_purpose_label: str,
):
    mode_predicted_label = find_mode_predicted_label(db, user_id, trip, section)

    writer.writerow(
        [
            user_id.hex(),
            trip["_id"],
            section["_id"],
            trip["data"]["start_fmt_time"],
            trip["data"]["end_fmt_time"],
            trip["data"]["duration"],
            section["data"]["start_fmt_time"],
            section["data"]["end_fmt_time"],
            section["data"]["duration"],
            trip["data"]["start_loc"]["coordinates"][0],
            trip["data"]["start_loc"]["coordinates"][1],
            trip["data"]["end_loc"]["coordinates"][0],
            trip["data"]["end_loc"]["coordinates"][1],
            trip["data"]["distance"],
            section["data"]["start_loc"]["coordinates"][0],
            section["data"]["start_loc"]["coordinates"][1],
            section["data"]["end_loc"]["coordinates"][0],
            section["data"]["end_loc"]["coordinates"][1],
            section["data"]["distance"],
            mode_predicted_label,
            manual_mode_label,
            manual_purpose_label,
        ]
    )


def extract_traces(
    db: database.Database,
    section: dict,
    writer_traces,
    user_id: bson.Binary,
    trip: dict,
    refresh_session_if_needed: Callable[[], None],
):
    section_traces = db.Stage_analysis_timeseries.find(
        {
            "metadata.key": "analysis/recreated_location",
            "data.section": section["_id"],
        },
        no_cursor_timeout=True,
    )

    for trace in section_traces:
        refresh_session_if_needed()
        writer_traces.writerow(
            [
                user_id.hex(),
                trip["_id"],
                section["_id"],
                trace["data"]["fmt_time"],
                trace["data"]["latitude"],
                trace["data"]["longitude"],
                trace["data"]["ts"],
                trace["data"]["altitude"],
                trace["data"]["distance"],
                trace["data"]["speed"],
                trace["data"]["heading"],
                trace["data"]["mode"],
            ]
        )


def extract_sections_and_traces(
    user_id: bson.Binary,
    db: database.Database,
    writer,
    writer_traces,
    refresh_session_if_needed: Callable[[], None],
):
    trips = db.Stage_analysis_timeseries.find(
        {"user_id": user_id, "metadata.key": "analysis/cleaned_trip"},
        no_cursor_timeout=True,
    )
    for trip in trips:
        refresh_session_if_needed()
        sections = db.Stage_analysis_timeseries.find(
            {
                "user_id": user_id,
                "metadata.key": "analysis/cleaned_section",
                "data.trip_id": trip["_id"],
            },
            no_cursor_timeout=True,
        )

        manual_mode_label = find_manual_mode_label(db, trip)
        manual_purpose_label = find_manual_purpose_label(db, trip)

        for section in sections:
            refresh_session_if_needed()
            extract_sections(
                db,
                user_id,
                trip,
                section,
                writer,
                manual_mode_label,
                manual_purpose_label,
            )
            extract_traces(
                db, section, writer_traces, user_id, trip, refresh_session_if_needed
            )


def extract(
    db: database.Database,
    studies_names: List[str],
    ignored_tokens: List[str],
    refresh_session_if_needed: Callable[[], None],
) -> None:
    users = get_users(db, studies_names, ignored_tokens, refresh_session_if_needed)
    save_users(users)

    with open("traisimove_database.csv", "w") as output_file, open(
        "traisimove_traces.csv", "w"
    ) as output_traces_file:
        writer = csv.writer(output_file)
        writer_traces = csv.writer(output_traces_file)
        writer.writerow(headers)
        writer_traces.writerow(headers_traces)
        for user in users:
            user_id = user["user_id"]
            print("Working on : ", user_id.hex())
            extract_sections_and_traces(
                user_id, db, writer, writer_traces, refresh_session_if_needed
            )

    surveys_answers = extract_surveys_answers(users, db, refresh_session_if_needed)
    with open("traisimove_surveys.json", "w") as output_file:
        json.dump(surveys_answers, output_file)
