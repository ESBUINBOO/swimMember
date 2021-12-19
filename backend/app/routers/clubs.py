"""
this is keycloak administration! If every club is a realm, this is really sensitive!
"""
import os
import sys
import logging
import base64
from typing import Optional, List, Union
from fastapi import FastAPI, Header, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter
from bson import ObjectId
from enum import Enum
sys.path.append("app")
from mongo_handler.MongoHandler import MongoHandler
from models.club import Clubs, Groups
from helper.read_config import CONFIGS
logger = logging.getLogger('ROUTER_MEMBERS_API_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

router = APIRouter()


@router.post('/api/v1/club/', tags=["clubs"])
async def create_club(club: Clubs, contact_person: Optional[str] = None):
    return JSONResponse(status_code=200, content={"result": True, "message": "not implemented yet", "detail": None})


@router.delete('/api/v1/club/{club_id}', tags=["clubs"])
async def delete_club(club_id: str):
    return JSONResponse(status_code=200, content={"result": True, "message": "not implemented yet", "detail": None})


@router.get('/api/v1/club/{club_id}', tags=["clubs"])
async def get_club_by_club_id(club_id: str):
    return JSONResponse(status_code=200, content={"result": True, "message": "not implemented yet", "detail": None})


@router.get('/api/v1/club/', tags=["clubs"])
async def get_all_clubs():
    return JSONResponse(status_code=200, content={"result": True, "message": "not implemented yet", "detail": None})


@router.put('/api/v1/club/{club_id}', tags=["clubs"])
async def update_club(club_id: str, club: Clubs, contact_person: Clubs.contact_person):
    return JSONResponse(status_code=200, content={"result": True, "message": "not implemented yet", "detail": None})
