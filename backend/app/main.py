import os
import sys
import logging
import base64
from typing import Optional, List, Union
from fastapi import FastAPI, Header, Query
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from enum import Enum
sys.path.append("app")
# from backend.app.selenium_handler.selenium_handler import SeleniumHandler
from mongo_handler.MongoHandler import MongoHandler
from routers import members_and_roles, clubs_and_groups, swimmers, meetings
from internal import admin

logger = logging.getLogger('FAST_API_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

mongo_handler = MongoHandler()
print(__name__, id(mongo_handler))
# keycloak_handler = KeycloakHandler(server_url=KC_URL, client_id=CLIENT_ID, client_secret_key=CLIENT_SECRET, realm_name=REALM)

app = FastAPI()
app.include_router(members_and_roles.router)
app.include_router(clubs_and_groups.router)
app.include_router(swimmers.router)
app.include_router(meetings.router)
app.include_router(admin.router)


@app.get('/api/v1/health')
def health_check():
    return {"message": "Hello World from fast api service"}


