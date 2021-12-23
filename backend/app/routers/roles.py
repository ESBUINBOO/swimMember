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
from models.member import Member, Address
from models.role import Role
from keycloak_handler.KeycloakHandler import KeycloakHandler, KeycloakAdminHandler
from keycloak.exceptions import KeycloakError
from helper.read_config import CONFIGS
from models.club import Clubs

logger = logging.getLogger('ROUTER_MEMBERS_API_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

router = APIRouter()
print(__name__)
print(CONFIGS)
mongo_handler = MongoHandler(uri=CONFIGS["MONGO_URI"], db_name=CONFIGS["MONGODB_NAME"])
keycloak_handler = KeycloakHandler(server_url=CONFIGS["KEYCLOAK_SERVER"],
                                   client_id=CONFIGS["CLIENT_ID"],
                                   realm_name=CONFIGS["REALM"],
                                   client_secret_key=CONFIGS["CLIENT_SECRET_KEY"])
keycloak_admin_handler = KeycloakAdminHandler(server_url=CONFIGS["KEYCLOAK_SERVER"],
                                              realm_name=CONFIGS["REALM"],
                                              password=CONFIGS["KC_ADMIN_PW"])


@router.get('/api/v1/role/', tags=["role"])
async def get_all_roles():
    """

    :return:
    """
    client_roles = keycloak_admin_handler.get_client_roles(client_id=keycloak_admin_handler.get_client_id(client_name="sm"))
    return JSONResponse(status_code=200,
                        content={"result": True, "message": client_roles, "detail": "found {} role(s)".format(len(client_roles))})


@router.delete('/api/v1/role/{role_name}', tags=["role"])
async def delete_role(role_name: str):
    """
    deletes a role in client
    :param role_name:
    """
    # todo: this api should be secured like token, basic auth, etc.
    #  cuz, its not gud, that every1 can conusme this kind of apis
    try:
        kc_result = keycloak_admin_handler.delete_client_role_(
            client_role_id=keycloak_admin_handler.get_client_id(client_name="sm"),
            role_name=role_name)
        if isinstance(kc_result, tuple):  # index 0 = status code, 1 = message
            return JSONResponse(status_code=kc_result[0], content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        return JSONResponse(status_code=200, content={"result": True, "message": kc_result, "detail": None})
    except Exception as err:
        logger.error('Error in delete_role() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": err})


@router.post('/api/v1/role/', tags=["role"])
async def create_role(role: Role):
    """
    creates a new role in keycloak realm
    \f
    :param role: class of Roles
    """
    # todo: this api should be secured like token, basic auth, etc.
    #  cuz, its not gud, that every1 can conusme this kind of apis
    try:
        kc_result = keycloak_admin_handler.create_client_role_(
            client_role_id=keycloak_admin_handler.get_client_id(client_name="sm"),
            payload=jsonable_encoder(role))
        logger.debug("kc_result: {}".format(kc_result))
        if isinstance(kc_result, tuple):  # index 0 = status code, 1 = message
            return JSONResponse(status_code=kc_result[0], content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        return JSONResponse(status_code=201, content={"result": True, "message": jsonable_encoder(kc_result), "detail": None})
    except Exception as err:
        logger.error('Error in create_role() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": err})
