import os
import sys
import logging
import base64
from typing import Optional, List, Union
from fastapi import FastAPI, Header, Query
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter
from bson import ObjectId
from enum import Enum
sys.path.append("app")
from mongo_handler.MongoHandler import MongoHandler

logger = logging.getLogger('ROUTER_MEMBERS_API_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

router = APIRouter()
mongo_handler = MongoHandler()
print(__name__, id(mongo_handler))


class Timing(str, Enum):
    manual = "HANDZEIT"
    automatic = "AUTOMATISCH"
    semi_automatic = "HALBAUTOMATISCH"


class Organizer(BaseModel):
    club = str
    contact = str
    email = str


class Meeting(BaseModel):
    """
    Do your GET Requests against the members path, its the same :-)
    """
    name: str
    date: list
    location: str
    course: str
    timing: Timing
    sections: list
    organizer: Organizer


@router.post('/api/v1/meeting/', tags=["meeting"])
async def create_meeting(meeting: Meeting):
    """
    creates a new swimmer.
    :return: member object
    """
    try:
        pass
        return
    except Exception as err:
        logger.error('Error in create_meeting() err: {}'.format(err))
        return {"message": "something went wrong"}


@router.put('/api/v1/meeting/{meeting_id}', tags=["meeting"])
async def update_meeting(meeting_id: str):
    pass


@router.delete('/api/v1/meeting/{meeting_id}', tags=["meeting"])
async def delete_meeting(meeting_id: str):
    pass


@router.get('/api/v1/meeting/{meeting_id}', tags=["meeting"])
async def get_one_meeting_by_meeting_id(meeting_id: str):
    pass


@router.get('/api/v1/meeting/', tags=["meeting"])
async def get_all_meetings(date: Optional[str] = Query(None),
                           name: Optional[str] = Query(None),
                           detailed: bool = Query(False)):
    query = {}
    fields_to_hide = {"meeting_definition.Wertungen": 0, "meeting_definition.Wettkaempfe": 0,
                      "meeting_definition.Pflichtzeiten": 0, "created": 0, "updated": 0, "file_hash": 0}
    if date:
        query["meeting_definition.Abschnitte.abschnitts_datum"] = date
    if name:
        query["meeting_definition.Abschnitte.abschnitts_datum"] = name
    if detailed:
        fields_to_hide = None
    meetings = mongo_handler.find_many_docs(col="meetings", query=query, fields_to_hide=fields_to_hide)
    return {"message": meetings}
