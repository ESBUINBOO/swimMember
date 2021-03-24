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


class Clubs(str, Enum):
    # todo: Enums aus config auslesen
    # todo: contact_person sollte ObjectId sein
    w98 = "Wassersportfreunde von 1989"
    test = "test"
    contact_person: Optional[str] = None


class Groups(BaseModel):
    group_name: str
    club_name: Clubs
    coaches: Optional[list] = None
    members: Optional[list] = None


@router.post('/api/v1/club/', tags=["clubs"])
async def create_club(club: Clubs, contact_person: Optional[str] = None):
    # todo: contact_person sollte ObjectId sein, nicht str
    obj = {}
    if contact_person:
        obj["contact_person"] = ObjectId(contact_person)
    obj["name"] = club.value
    result = mongo_handler.insert_doc(col="clubs", obj=obj)
    return {"message": str(result)}


@router.delete('/api/v1/club/{club_id}', tags=["clubs"])
async def delete_club(club_id: str):
    result = mongo_handler.delete_doc(col="clubs", query={"_id": ObjectId(club_id)})
    return {"message": result}


@router.get('/api/v1/club/{club_id}', tags=["clubs"])
async def get_club_by_club_id(club_id: str):
    result = mongo_handler.find_one_doc(col="clubs", query={"_id": ObjectId(club_id)})
    return {"message": result}


@router.get('/api/v1/club/', tags=["clubs"])
async def get_all_clubs():
    clubs = mongo_handler.find_many_docs(col="clubs", query={})
    return {"message": clubs}


@router.put('/api/v1/club/{club_id}', tags=["clubs"])
async def update_club(club_id: str, club: Clubs, contact_person: Clubs.contact_person):
    update_query = {"$set": dict(club)}
    modified_docs = mongo_handler.update_one_doc(col="clubs", _filter={"_id": ObjectId(club_id)}, query=update_query)
    return {"message": modified_docs}


# groups
@router.post('/api/v1/group/', tags=["groups"])
async def create_group(group: Groups):
    obj = {}
    if group.coaches:
        obj["coaches"] = [i for i in group.coaches]
    if group.members:
        obj["members"] = [ObjectId(i) for i in group.coaches]
    obj["group_name"] = group.group_name
    result = mongo_handler.insert_doc(col="groups", obj=obj)
    return {"message": str(result)}


@router.get('/api/v1/group/', tags=["groups"])
async def get_all_groups():
    clubs = mongo_handler.find_many_docs(col="groups", query={})
    return {"message": clubs}


@router.get('/api/v1/group/{group_id}', tags=["groups"])
async def get_all_groups(group_id: str):
    groups = mongo_handler.find_one_doc(col="groups", query={"_id": ObjectId(group_id)})
    return {"message": groups}


@router.delete('/api/v1/group/{group_id}', tags=["groups"])
async def delete_group(group_id: str):
    result = mongo_handler.delete_doc(col="groups", query={"_id": ObjectId(group_id)})
    return {"message": result}


@router.put('/api/v1/group/{group_id}', tags=["groups"])
async def update_group(group_id: str, members: Optional[list], coaches: Optional[list], insert: bool):
    # todo: concat die queries zu einem
    # todo: die if anweisungen verschönern
    # Array Operators: https://docs.mongodb.com/manual/reference/operator/update-array/
    _filter = {"_id": ObjectId(group_id)}
    # test_update_query = {"$push": {"members": {"$each": []}}}
    # test = {"$addtoSet": {"members": {"$each": []}}}
    update_query = {}
    modified_docs = 0
    if insert:
        array_update_operator = "$addToSet"  # "$push"
        array_update_operator_helper = "$each"
    else:
        array_update_operator = "$pull"
        array_update_operator_helper = "$in"
    if members:
        field = "members"
        sliced_query = {field: {array_update_operator_helper: [ObjectId(i) for i in members]}}

        update_query[array_update_operator] = sliced_query
        print("update_query: ", update_query)
        modified_docs = mongo_handler.update_one_doc(col="groups", _filter=_filter, query=update_query)
    if coaches:
        field = "coaches"
        sliced_query = {field: {array_update_operator_helper: [ObjectId(i) for i in coaches]}}
        update_query[array_update_operator] = sliced_query
        print("update_query: ", update_query)
        modified_docs = mongo_handler.update_one_doc(col="groups", _filter=_filter, query=update_query)

    return {"message": "modified_count {}".format(modified_docs)}