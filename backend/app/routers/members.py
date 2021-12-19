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
from models.member import Member, Roles, Address
from keycloak_handler.KeycloakHandler import KeycloakHandler, KeycloakAdminHandler
from keycloak.exceptions import KeycloakError
from helper.read_config import CONFIGS

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
print(id(mongo_handler))

# todo: those apis are nested with keylcoak. If u create a role here, we need to do it in keycloak also


@router.post('/api/v1/member/', tags=["member"])
async def create_member(member: Member):
    """
    creates a new member
    :return: member object
    """
    try:
        # todo: member information should be encrypted with a club / realm key
        # check if role exists
        role_exists = keycloak_admin_handler.get_client_role_(
            client_id=keycloak_admin_handler.get_client_id(client_name="sm"),
            role_name=member.role)
        if isinstance(role_exists, tuple):  # index 0 = status code, 1 = message
            return JSONResponse(status_code=role_exists[0], content={"result": False, "message": "keycloak error", "detail": role_exists[1]})
        doc_id = mongo_handler.insert_doc(col="members", query=jsonable_encoder(member))
        keycloak_user = {"attributes":
                             {"mongo_id": str(doc_id), "mobile_phone_number": member.mobile_phone_number},
                         "credentials": [{"type": "Password", "value": "test"}],
                         "username": member.firstname + "." + member.lastname,
                         "firstName": member.firstname,
                         "lastName": member.lastname,
                         "realmRoles": [jsonable_encoder(member.role)],
                         "enabled": False,
                         "requiredActions": ["UPDATE_PASSWORD"]}
        kc_result = keycloak_admin_handler.create_user_(payload=keycloak_user, exist_ok=False)
        if isinstance(kc_result, tuple):  # index 0 = status code, 1 = message
            mongo_handler.delete_doc(col="members", query={"_id": doc_id})
            return JSONResponse(status_code=kc_result[0], content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        return JSONResponse(status_code=201, content={"result": True, "message": kc_result, "detail": None})
    except Exception as err:
        logger.error('Error in create_user() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": err})


@router.put('/api/v1/member/{member_id}', tags=["member"])
async def update_member(member_id: str, member: Member):
    """
    update an existing member
    """
    # todo: this must be better, like maybe i dont want to update the whole user object, just add a phone number
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
    """
    :param member_id: keycloak user id
    """
    user = keycloak_admin_handler.get_user_(user_id=member_id)
    if isinstance(user, tuple):  # index 0 = status code, 1 = message
        return JSONResponse(status_code=user[0],
                            content={"result": False, "message": "keycloak error", "detail": user[1]})
    logger.debug(user)
    mongo_db_id = user["attributes"]["mongo_id"][0]
    kc_result = keycloak_admin_handler.delete_user_(user_id=member_id)
    if isinstance(kc_result, tuple):  # index 0 = status code, 1 = message
        return JSONResponse(status_code=kc_result[0],
                            content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
    result = mongo_handler.delete_doc(col="members", query={"_id": ObjectId(mongo_db_id)})
    return JSONResponse(status_code=200, content={"result": True, "message": "", "detail": "deleted user with id {}".format(member_id)})


@router.get('/api/v1/member/{user_name}', tags=["member"])
async def get_member_by_user_name(user_name: str, details: bool = False):
    kc_result = keycloak_admin_handler.get_user_id_(username=user_name)
    if isinstance(kc_result, tuple):  # index 0 = status code, 1 = message
        return JSONResponse(status_code=kc_result[0],
                            content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
    user_info = keycloak_admin_handler.get_user_(user_id=kc_result)
    if kc_result is None:
        return JSONResponse(status_code=404,
                            content={"result": True,
                                     "message": "not found",
                                     "detail": "user with user name {} not found".format(user_name)})
    detail = None
    if details:
        mongo_id = user_info["attributes"]["mongo_id"][0]
        detail = mongo_handler.find_one_doc(col="members", query={"_id": ObjectId(mongo_id)})
    return JSONResponse(status_code=200, content={"result": True, "message": user_info, "detail": detail})


@router.get('/api/v1/member/', tags=["member"])
async def get_all_members(lastname: Optional[str] = Query(None),
                          firstname: Optional[str] = Query(None),
                          details: bool = False):
    """
    mongoDB find limit default = 50
    :return:
    """
    kc_query = {}
    if lastname:
        kc_query["lastName"] = lastname
    if firstname:
        kc_query["lastName"] = lastname
    kc_result = keycloak_admin_handler.get_users_(query=kc_query)
    if isinstance(kc_result, tuple):  # index 0 = status code, 1 = message
        return JSONResponse(status_code=kc_result[0],
                            content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
    detail = None
    if details:
        # todo: think about data structure. Maybe its wise to put the mongo docs into details as list.
        #  Marcel nach Rat fragen
        detail = []
        for user_info in kc_result:
            mongo_id = user_info["attributes"]["mongo_id"][0]
            query = {"_id": ObjectId(mongo_id)}
            member = mongo_handler.find_one_doc(col="members", query=query)
            user_info["details"] = member
            detail.append(member)
    return JSONResponse(status_code=200, content={"result": True, "message": kc_result, "details": detail})
