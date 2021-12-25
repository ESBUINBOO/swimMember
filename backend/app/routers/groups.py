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
from models.group import Groups, Group
from helper.read_config import CONFIGS
logger = logging.getLogger('ROUTER_GROUPS_API_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

router = APIRouter()
keycloak_admin_handler = KeycloakAdminHandler(server_url=CONFIGS["KEYCLOAK_SERVER"],
                                              realm_name=CONFIGS["REALM"],
                                              password=CONFIGS["KC_ADMIN_PW"])


@router.post('/api/v1/group/', tags=["groups"])
async def create_group(group: Group, parent_id: Optional[str] = None):
    try:
        kc_result = keycloak_admin_handler.create_group_(payload=jsonable_encoder(group),
                                                         parent=parent_id,
                                                         skip_exists=False)
        if isinstance(kc_result, tuple):
            return JSONResponse(status_code=kc_result[0],
                                content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        group_id = keycloak_admin_handler.get_group_by_path(path="/" + group.name)["id"]
        return JSONResponse(status_code=201,
                            content={"result": True,
                                     "message": group_id,
                                     "detail": None})
    except Exception as err:
        logger.debug(traceback.print_exc())
        logger.error('Error in create_group() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})


@router.get('/api/v1/group/', tags=["groups"])
async def get_all_groups():
    try:
        groups = keycloak_admin_handler.get_groups_()
        return JSONResponse(status_code=200,
                            content={"result": True,
                                     "message": groups,
                                     "detail": "found {} groups".format(len(groups))})
    except Exception as err:
        logger.debug(traceback.print_exc())
        logger.error('Error in get_all_groups() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})


@router.get('/api/v1/group/{group_id}', tags=["groups"])
async def get_group_by_id(group_id: str):
    try:
        group = keycloak_admin_handler.get_group_(group_id=group_id)
        logger.debug("group: {}".format(group))
        if isinstance(group, tuple):
            return JSONResponse(status_code=group[0],
                                content={"result": False, "message": "keycloak error", "detail": group[1]})
        return JSONResponse(status_code=200,
                            content={"result": True,
                                     "message": group,
                                     "detail": None})
    except Exception as err:
        logger.error('Error in get_group_by_id() err: {}'.format(err))
        logger.debug(traceback.print_exc())
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})


@router.get('/api/v1/group/{group_id}/members', tags=["groups"])
async def get_group_members(group_id: str):
    try:
        kc_result = keycloak_admin_handler.get_group_members_(group_id=group_id)
        if isinstance(kc_result, tuple):
            return JSONResponse(status_code=kc_result[0],
                                content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        return JSONResponse(status_code=200,
                            content={"result": True,
                                     "message": kc_result,
                                     "detail": "found {} members".format(len(kc_result))})
    except Exception as err:
        logger.error('Error in delete_group() err: {}'.format(err))
        logger.debug(traceback.print_exc())
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})


@router.delete('/api/v1/group/{group_id}', tags=["groups"])
async def delete_group(group_id: str):
    try:
        kc_result = keycloak_admin_handler.delete_group_(group_id=group_id)
        if isinstance(kc_result, tuple):
            return JSONResponse(status_code=kc_result[0],
                                content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        return JSONResponse(status_code=204,
                            content={"result": True,
                                     "message": None,
                                     "detail": None})
    except Exception as err:
        logger.error('Error in delete_group() err: {}'.format(err))
        logger.debug(traceback.print_exc())
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})


@router.patch('/api/v1/group/{group_id}', tags=["groups"])
async def update_group(group_id: str):
    return JSONResponse(status_code=200,
                        content={"result": True, "message": "not implemented yet", "detail": "under construction x)"})


@router.patch('/api/v1/group/{group_id}/{member_id}', tags=["groups"])
async def add_member_to_group(group_id: str, member_id: str):
    try:
        kc_result = keycloak_admin_handler.group_user_add_(user_id=member_id, group_id=group_id)
        if isinstance(kc_result, tuple):
            return JSONResponse(status_code=kc_result[0],
                                content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        return JSONResponse(status_code=200,
                            content={"result": True,
                                     "message": None,
                                     "detail": None})
    except Exception as err:
        logger.error('Error in delete_group() err: {}'.format(err))
        logger.debug(traceback.print_exc())
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})


@router.delete('/api/v1/group/{group_id}/{member_id}', tags=["groups"])
async def delete_member_from_group(group_id: str, member_id: str):
    try:
        kc_result = keycloak_admin_handler.group_user_remove_(user_id=member_id, group_id=group_id)
        if isinstance(kc_result, tuple):
            return JSONResponse(status_code=kc_result[0],
                                content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        return JSONResponse(status_code=200,
                            content={"result": True,
                                     "message": None,
                                     "detail": None})
    except Exception as err:
        logger.error('Error in delete_group() err: {}'.format(err))
        logger.debug(traceback.print_exc())
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})
