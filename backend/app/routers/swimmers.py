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
from models.member import Member

logger = logging.getLogger('ROUTER_MEMBERS_API_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

router = APIRouter()
mongo_handler = MongoHandler()
print(__name__, id(mongo_handler))


class Swimmer(Member):
    """
    Do your GET Requests against the members path, its the same :-)
    """
    # todo: jedes member kann nur in 1 Gruppe sein. Members müssen in n-Gruppen vertreten sein,
    #  mit jeweils einer Rolle => {group_name: role}
    reg_id: int
    active: bool
    parents: Optional[List[str]] = None
    license: Optional[int] = None
    license_paid: Optional[bool] = None
    medical_certificate: Optional[str] = None
    group: Groups


@router.post('/api/v1/member/swimmer/', tags=["swimmer"])
async def create_swimmer(swimmer: Swimmer):
    """
    creates a new swimmer.
    :return: member object
    """
    try:

        _swimmer = dict(swimmer)
        _swimmer["address"] = dict(swimmer.address)   # you need this, because the key "address" is a BaseModel Object
                                                    # and pymongo cant insert it
        _swimmer["group"] = dict(swimmer.group)
        doc_id = mongo_handler.insert_doc(col="members", obj=_swimmer)
        return {"message": str(doc_id)}
    except Exception as err:
        logger.error('Error in create_user() err: {}'.format(err))
        return {"message": "something went wrong"}


@router.put('/api/v1/member/swimmer/{swimmer_id}', tags=["swimmer"])
async def update_swimmer(swimmer_id: str, swimmer: Swimmer):
    _swimmer = dict(swimmer)
    _swimmer["address"] = dict(swimmer.address)
    update_query = {"$set": _swimmer}
    _filter = {"_id": ObjectId(swimmer_id)}
    modified_docs = mongo_handler.update_one_doc(col="members", _filter=_filter, query=update_query)
    return {"message": "modified_count {}".format(modified_docs)}


