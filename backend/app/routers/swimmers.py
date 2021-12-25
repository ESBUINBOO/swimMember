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
from models.member import Member, Swimmer
from keycloak_handler.KeycloakHandler import KeycloakHandler, KeycloakAdminHandler
from helper.read_config import CONFIGS

logger = logging.getLogger('ROUTER_MEMBERS_API_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

router = APIRouter()
mongo_handler = MongoHandler()
keycloak_admin_handler = KeycloakAdminHandler(server_url=CONFIGS["KEYCLOAK_SERVER"],
                                              realm_name=CONFIGS["REALM"],
                                              password=CONFIGS["KC_ADMIN_PW"])


@router.post('/api/v1/swimmer/', tags=["swimmer"])
async def create_swimmer(swimmer: Swimmer):
    """
    creates a new member
    :return: member object
    """
    try:
        # todo: member information should be encrypted with a club / realm key
        # todo: how to avoid creating a member as swimmer here?
        # check if role exists
        role_exists = keycloak_admin_handler.get_client_role_(
            client_id=keycloak_admin_handler.get_client_id(client_name="sm"),
            role_name=swimmer.role)
        if isinstance(role_exists, tuple):  # index 0 = status code, 1 = message
            return JSONResponse(status_code=role_exists[0], content={"result": False, "message": "keycloak error", "detail": role_exists[1]})
        group_exists = keycloak_admin_handler.get_group_(group_id=swimmer.group)
        if isinstance(group_exists, tuple):  # index 0 = status code, 1 = message
            return JSONResponse(status_code=group_exists[0], content={"result": False, "message": "keycloak error", "detail": group_exists[1]})
        doc_id = mongo_handler.insert_doc(col="members", query=jsonable_encoder(swimmer))
        client_id = keycloak_admin_handler.get_client_id(client_name="sm")
        keycloak_user = {"attributes": {
            "mongo_id": str(doc_id),
            "mobile_phone_number": jsonable_encoder(swimmer.phone_numbers["mobile"])},
            "credentials": [{"type": "Password", "value": "test", "temporary": True}],
            "username": swimmer.firstname + "." + swimmer.lastname,
            "firstName": swimmer.firstname,
            "lastName": swimmer.lastname,
            # "groups": [member.group],
             # this is buggy -> Keycloak Failure
             # see https://stackoverflow.com/questions/49818453/client-roles-havent-assigned-during-creating-new-user-in-keycloak
             # "clientRoles": {client_id: [role_exists]},
             # "clientRoles": {client_id: [role_exists["id"]]},
             "enabled": False,
             "requiredActions": ["UPDATE_PASSWORD"]}
        logger.debug(keycloak_user)
        kc_result = keycloak_admin_handler.create_user_(payload=keycloak_user, exist_ok=False)
        if isinstance(kc_result, tuple):  # index 0 = status code, 1 = message
            mongo_handler.delete_doc(col="members", query={"_id": doc_id})
            return JSONResponse(status_code=kc_result[0], content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        # add Client Roles
        update_result = keycloak_admin_handler.assign_client_role_(user_id=kc_result, client_id=client_id, roles=role_exists)
        if isinstance(update_result, tuple):  # index 0 = status code, 1 = message
            keycloak_admin_handler.delete_user_(user_id=kc_result)
            return JSONResponse(status_code=kc_result[0], content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        # add user to group
        update_result = keycloak_admin_handler.group_user_add_(user_id=kc_result, group_id=swimmer.group)
        if isinstance(update_result, tuple):  # index 0 = status code, 1 = message
            keycloak_admin_handler.delete_user_(user_id=kc_result)
            return JSONResponse(status_code=kc_result[0], content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        return JSONResponse(status_code=201, content={"result": True, "message": kc_result, "detail": None})
    except Exception as err:
        logger.error('Error in create_user() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": err})


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


@router.get('/api/v1/member/swimmer/', tags=["swimmer"])
async def get_all_swimmers(swimmer: Swimmer):
    """

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
