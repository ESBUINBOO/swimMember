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
                           organizer_name: Optional[str] = Query(None)):
    query = {}
    if date:
        query["meta.date"] = date
    if name:
        query["meta.meeting_name"] = name
    if organizer_name:
        query["meta.organizer.club"] = organizer_name
    members = mongo_handler.find_many_docs(col="meetings", query=query)
    return {"message": members}
