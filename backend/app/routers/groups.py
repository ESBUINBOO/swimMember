import os
import sys
import logging
import base64
import traceback
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
from keycloak_handler.KeycloakHandler import KeycloakHandler, KeycloakAdminHandler
from models.club import Clubs
from models.group import Groups
from helper.read_config import CONFIGS
logger = logging.getLogger('ROUTER_MEMBERS_API_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

router = APIRouter()
keycloak_admin_handler = KeycloakAdminHandler(server_url=CONFIGS["KEYCLOAK_SERVER"],
                                              realm_name=CONFIGS["REALM"],
                                              password=CONFIGS["KC_ADMIN_PW"])


@router.post('/api/v1/group/', tags=["groups"])
async def create_group(group: Groups, parent_id: Optional[str] = None):
    try:
        kc_result = keycloak_admin_handler.create_group_(payload=jsonable_encoder(group), parent=parent_id, skip_exists=False)
        if isinstance(kc_result, tuple):
            return JSONResponse(status_code=kc_result[0],
                                content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        return JSONResponse(status_code=201,
                            content={"result": True,
                                     "message": "group {} successfully created".format(group.name),
                                     "detail": None})
    except Exception as err:
        logger.debug(traceback.print_exc())
        logger.error('Error in create_group() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})


@router.get('/api/v1/group/', tags=["groups"])
async def get_all_groups():
    pass


@router.get('/api/v1/group/{group_id}', tags=["groups"])
async def get_group_by_id(group_id: str):
    pass


@router.delete('/api/v1/group/{group_id}', tags=["groups"])
async def delete_group(group_id: str):
    pass


@router.patch('/api/v1/group/{group_id}', tags=["groups"])
async def update_group(group_id: str):
    pass


@router.patch('/api/v1/group/{group_id}/{member_id}', tags=["groups"])
async def add_member_to_group(group_id: str, member_id: str):
    pass


@router.delete('/api/v1/group/{group_id}/{member_id}', tags=["groups"])
async def delete_member_from_group(group_id: str, member_id: str):
    pass
