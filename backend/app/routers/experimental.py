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
from models.member import Member, Address, Swimmer, Coach
from models.experimental import MemberCategories
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
members_dict = {
      "firstname": "Max",
      "lastname": "Mustermann",
      "birth": "01.01.2000",
      "gender": "Male",
      "address": {
        "street": "Elmstreet",
        "house_number": "42",
        "zipcode": 123456,
        "town": "Entenhausen"
      },
      "emails": [
        "test@test.de"
      ],
      "phone_numbers": {
        "mobile": "+49123456"
      },
      "member_since": 1898,
      "role": "Parent"
    }
swimmer_dict = members_dict.copy()
swimmer_dict.update({"role": "Swimmer", "reg_id": 0, "active": False, "group": ""})
coach_dict = members_dict.copy()
coach_dict.update({"role": "Coach", "coaching_license": "A", "license_valid_to": "05/2025"})
case_cats = {MemberCategories.member:  jsonable_encoder(Member(**members_dict)),
             MemberCategories.swimmer: jsonable_encoder(Swimmer(**swimmer_dict)),
             MemberCategories.coach: jsonable_encoder(Coach(**coach_dict))}


@router.post('/api/v2/member/', tags=["experimental"])
async def create_member(member_category: MemberCategories, payload: dict):
    """
    creates a new member. The needed payload can be found in the MemberCategories
    :return: member object
    """
    try:
        try:
            if member_category == MemberCategories.member:
                member = Member(**payload)
            elif member_category == MemberCategories.swimmer:
                member = Swimmer(**payload)
            elif member_category == MemberCategories.coach:
                member = Coach(**payload)
            else:
                return JSONResponse(status_code=400,
                                    content={"result": False,
                                             "message": "Bad Request",
                                             "detail": "no valid member category"})
        except Exception as err:
            return JSONResponse(status_code=400,
                                content={"result": False,
                                         "message": "Bad Request",
                                         "detail": str(err)})
        # check if role exists
        role_exists = keycloak_admin_handler.get_client_role_(
            client_id=keycloak_admin_handler.get_client_id(client_name="sm"),
            role_name=member.role)
        if isinstance(role_exists, tuple):  # index 0 = status code, 1 = message
            return JSONResponse(status_code=role_exists[0],
                                content={"result": False, "message": "keycloak error", "detail": role_exists[1]})
        group_exists = keycloak_admin_handler.get_group_(group_id=member.group)
        if isinstance(group_exists, tuple):  # index 0 = status code, 1 = message
            return JSONResponse(status_code=group_exists[0],
                                content={"result": False, "message": "keycloak error", "detail": group_exists[1]})
        doc_id = mongo_handler.insert_doc(col="members", query=jsonable_encoder(member))
        client_id = keycloak_admin_handler.get_client_id(client_name="sm")
        keycloak_user = {"attributes": {
            "mongo_id": str(doc_id),
            "mobile_phone_number": jsonable_encoder(member.phone_numbers["mobile"])},
            "credentials": [{"type": "Password", "value": "test", "temporary": True}],
            "username": member.firstname + "." + member.lastname,
            "firstName": member.firstname,
            "lastName": member.lastname,
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
        update_result = keycloak_admin_handler.group_user_add_(user_id=kc_result, group_id=member.group)
        if isinstance(update_result, tuple):  # index 0 = status code, 1 = message
            keycloak_admin_handler.delete_user_(user_id=kc_result)
            return JSONResponse(status_code=kc_result[0], content={"result": False, "message": "keycloak error", "detail": kc_result[1]})
        return JSONResponse(status_code=201, content={"result": True, "message": kc_result, "detail": None})
    except Exception as err:
        logger.error('Error in create_user() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": err})


@router.get('/api/v2/member/', tags=["experimental"])
async def get_member_categories():
    try:
        message = {str(k): v for (k, v) in case_cats.items()}
        return JSONResponse(status_code=200, content={"result": True,
                                                      "message": message,
                                                      "detail": None})
    except Exception as err:
        logger.error('Error in create_user() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": err})
