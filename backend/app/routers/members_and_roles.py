import os
import sys
import logging
import base64
from typing import Optional, List, Union
from fastapi import FastAPI, Header, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter
from bson import ObjectId
from enum import Enum
sys.path.append("app")
from mongo_handler.MongoHandler import MongoHandler
from helper.read_config import CONFIGS
from routers.clubs_and_groups import Clubs

logger = logging.getLogger('ROUTER_MEMBERS_API_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

router = APIRouter()
print(__name__)
print(CONFIGS)
mongo_handler = MongoHandler(uri=CONFIGS["MONGO_URI"], db_name=CONFIGS["MONGODB_NAME"])
print(id(mongo_handler))


class Roles(str, Enum):
    swimmer = "Schwimmer"
    parent = "Elternteil"
    coach = "Trainer"
    head_coach = "Head Coach"
    swimming_attendant = "Schwimmwart"


class Address(BaseModel):
    street: str
    house_number: str
    zipcode: int
    town: str


class Member(BaseModel):
    # todo: EMailStr zum Laufen bekommen
    firstname: str
    lastname: str
    birth: str  # should be Datetime
    gender: str
    address: Address
    emails: List[str]
    phone_numbers: Optional[List[str]] = None
    member_since: Optional[str] = None
    role: Roles


@router.post('/api/v1/member/', tags=["member"])
async def create_member(member: Member):
    """
    creates a new member.
    :return: member object
    """
    # todo: i think its better to create the user in Keycloak =),
    #  or create member in DB and reference id to user attribute in KC Userss
    try:
        try:
            member = jsonable_encoder(member)
        except Exception as err:
            return JSONResponse(status_code=400,
                                content={"result": False, "message": "could not encode member", "detail": err})
        doc_id = mongo_handler.insert_doc(col="members", query=member)
        return JSONResponse(status_code=201, content={"result": True, "message": str(doc_id), "detail": None})
    except Exception as err:
        logger.error('Error in create_user() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": err})


@router.put('/api/v1/member/{member_id}', tags=["member"])
async def update_member(member_id: str, member: Member):
    member = jsonable_encoder(member)
    update_query = {"$set": member}
    _filter = {"_id": ObjectId(member_id)}
    modified_docs = mongo_handler.update_one_doc(col="members", _filter=_filter, query=update_query)
    return JSONResponse(status_code=200,
                        content={"result": True,
                                 "message": "",
                                 "detail": "modified {} object(s)".format(modified_docs.modified_count)})


@router.delete('/api/v1/member/{member_id}', tags=["member"])
async def delete_member(member_id: str):
    # todo: nicht jedes member wird eine member_reg_id haben, da er kein sportler ist
    result = mongo_handler.delete_doc(col="members", query={"_id": ObjectId(member_id)})
    return {"message": result}


@router.get('/api/v1/member/{member_id}', tags=["member"])
async def get_member_by_member_id(member_id: str):
    member = mongo_handler.find_one_doc(col="members", query={"_id": ObjectId(member_id)})
    return {"message": dict(member)}


@router.get('/api/v1/member/', tags=["member"])
async def get_all_members(lastname: Optional[str] = Query(None),
                          firstname: Optional[str] = Query(None),
                          reg_id: Optional[int] = Query(None)):
    """
    mongoDB find limit default = 50
    :return:
    """
    query = {}
    if lastname:
        query["lastname"] = lastname
    if firstname:
        query["firstname"] = firstname
    if reg_id:
        query["reg_id"] = reg_id
    members = mongo_handler.find_many_docs(col="members", query=query)
    return {"message": members}


# roles
@router.get('/api/v1/role/', tags=["role"])
async def get_all_roles():
    """

    :return:
    """
    roles = mongo_handler.find_many_docs(col="roles", query={})
    return {"message": roles}


@router.get('/api/v1/role/{role_id}', tags=["role"])
async def get_all_roles(role_id: str):
    """

    :return:
    """
    role = mongo_handler.find_one_doc(col="roles", query={"_id": ObjectId(role_id)})
    return {"message": dict(role)}


@router.delete('/api/v1/role/{role_id}', tags=["role"])
async def delete_role(role_id: str):
    result = mongo_handler.delete_doc(col="roles", query={"_id": ObjectId(role_id)})
    return {"message": result}


@router.post('/api/v1/role/', tags=["role"])
async def create_role(role: Roles):
    """
    :return: member object
    """
    try:
        obj = {"role_name": role.value}
        doc_id = mongo_handler.insert_doc(col="roles", obj=obj)
        return {"message": str(doc_id)}
    except Exception as err:
        logger.error('Error in create_role() err: {}'.format(err))
        return {"message": "something went wrong"}