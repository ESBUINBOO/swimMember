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
from models.club import Clubs, Groups
from helper.read_config import CONFIGS
logger = logging.getLogger('ROUTER_MEMBERS_API_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

router = APIRouter()

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