import os
import sys
import logging
import base64
from typing import Optional, List, Union
from fastapi import FastAPI, Header, Query
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
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
        # todo: create Keycloak User and add doc id to attributes
        _swimmer = jsonable_encoder(swimmer)
        logger.debug("_swimmer: {}".format(_swimmer))
        doc_id = mongo_handler.insert_doc(col="members", obj=_swimmer)
        return JSONResponse(status_code=201, content={"result": True, "message": str(doc_id), "detail": None})
    except Exception as err:
        logger.error('Error in create_user() err: {}'.format(err))
        JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": err})


@router.put('/api/v1/member/swimmer/{swimmer_id}', tags=["swimmer"])
async def update_swimmer(swimmer_id: str, swimmer: Swimmer):
    _swimmer = jsonable_encoder(swimmer)
    update_query = {"$set": _swimmer}
    _filter = {"_id": ObjectId(swimmer_id)}
    modified_docs = mongo_handler.update_one_doc(col="members", _filter=_filter, query=update_query).modified_count
    if modified_docs == 0:
        return JSONResponse(status_code=404,
                            content={"result": True,
                                     "message": "Not Found",
                                     "detail": "Swimmer with id {} not found".format(swimmer_id)})

    return JSONResponse(status_code=200,
                        content={"result": True,
                                 "message": "updated swimmer with id {}".format(swimmer_id),
                                 "detail": "modified_count {}".format(modified_docs)})


