from typing import Any, TypedDict

import bson
from pymongo import cursor, database

from extractor_users import User


class SurveyDocumentData(TypedDict):
    version: int
    ts: float
    jsonDocResponse: dict[str, Any]  # actual answers
    xmlResponse: str
    label: str
    fmt_time: str
    key: str
    name: str
    local_dt: object  # We don't care


class SurveyDocument(TypedDict):
    _id: bson.ObjectId
    Iduser_id: bson.Binary
    metadata: object  # We don't care
    data: SurveyDocumentData


class SurveyAnswer(TypedDict):
    user_id: str
    survey_name: str
    survey_version: int
    survey_answers: dict


def extract_surveys_answers(
    users: list[User],
    db: database.Database,
):
    surveys_answers = []
    for user in users:
        user_id = user["user_id"]
        survey_documents: cursor.Cursor[SurveyDocument] = db.Stage_timeseries.find(
            {"user_id": user_id, "metadata.key": "manual/demographic_survey"},
            no_cursor_timeout=True
        )
        for survey_document in survey_documents:
            survey_document_data = survey_document["data"]
            survey_answer = SurveyAnswer(
                user_id=user_id.hex(),
                survey_name=survey_document_data["name"],
                survey_version=survey_document_data["version"],
                survey_answers=survey_document_data["jsonDocResponse"],
            )
            surveys_answers.append(survey_answer)
    return surveys_answers
