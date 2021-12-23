import os
import sys
import logging
import base64
from typing import Optional, List, Union

import bson.errors
from fastapi import FastAPI, Header, Query, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter
from bson.objectid import ObjectId
# import bson
from enum import Enum
sys.path.append("app")
from mongo_handler.MongoHandler import MongoHandler
from dsv6_handler.Dsv6Handler import Dsv6FileHandler
from models.meeting import Meeting
from helper.utils import check_file_type, file_is_processable
from helper.proceed_dsv6_file import proceed_dsv6_file
logger = logging.getLogger('ROUTER_MEMBERS_API_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

router = APIRouter()
mongo_handler = MongoHandler()
print(__name__, id(mongo_handler))
dsv_handler = Dsv6FileHandler()


@router.post('/api/v1/meeting/', tags=["meeting"])
async def create_meeting(file: UploadFile = File(...)):
    """
    imports a DSV6 competition definition file
    :return:
    """
    try:
        contents = await file.read()
        file_name = file.filename
        file_type = check_file_type(file=contents)
        logger.debug(file_type)
        logger.debug(dsv_handler.file_dir)
        if not file_is_processable(file_type[1]):
            return JSONResponse(status_code=415,
                                content={"result": False,
                                         "message": "unsupported Media Type",
                                         "detail": "File type {} is not processable".format(file_type[1])})
        path = dsv_handler.file_dir + "/" + file_name
        logger.debug("path: {}".format(path))
        with open(path, "wb") as f:
            f.write(contents)
        doc_id = proceed_dsv6_file(dsv_file=path)
        if isinstance(doc_id, tuple):
            if doc_id[0] is False:
                return JSONResponse(status_code=409, content={"result": False,
                                                              "message": "Conflict",
                                                              "detail": doc_id[1]})

        return JSONResponse(status_code=201, content={"result": True,
                                                      "message": str(doc_id),
                                                      "detail": "successfully uploaded {}".format(file_name)})

    except Exception as err:
        logger.error('Error in create_meeting() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})


@router.patch('/api/v1/meeting/{meeting_id}', tags=["meeting"])
async def update_meeting(meeting_id: str, file: UploadFile = File(...)):
    """
    upload einer DSV6 Protokoll-Datei
    """
    try:
        mongo_id = mongo_handler.find_one_doc(col="meetings", query={"_id": ObjectId(meeting_id)})
        if mongo_id is None:
            return JSONResponse(status_code=404,
                                content={"result": True,
                                         "message": "Not found",
                                         "detail": "no meeting found with id {}".format(meeting_id)})
        contents = await file.read()
        file_name = file.filename
        file_type = check_file_type(file=contents)
        if not file_is_processable(file_type[1]):
            return JSONResponse(status_code=415,
                                content={"result": False,
                                         "message": "unsupported Media Type",
                                         "detail": "File type {} is not processable".format(file_type[1])})
        path = dsv_handler.file_dir + "/" + file_name
        logger.debug("path: {}".format(path))
        with open(path, "wb") as f:
            f.write(contents)
        doc_id = proceed_dsv6_file(dsv_file=path, obj_id=meeting_id)
        if isinstance(doc_id, tuple):
            if doc_id[0] is False:
                return JSONResponse(status_code=409, content={"result": False,
                                                              "message": "Conflict",
                                                              "detail": doc_id[1]})

        return JSONResponse(status_code=201, content={"result": True,
                                                      "message": "updated {} meeting(s)".format(doc_id.modified_count),
                                                      "detail": "successfully uploaded {}".format(file_name)})

    except Exception as err:
        logger.error('Error in create_meeting() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})


@router.delete('/api/v1/meeting/{meeting_id}', tags=["meeting"])
async def delete_meeting(meeting_id: str):
    """
    delete a meeting with given meeting_id. It deletes all associated files, too
    """
    # todo: get all associated files and delete them!
    query = {"_id": ObjectId(meeting_id)}
    results = mongo_handler.delete_doc(col="meetings", query=query)
    if isinstance(results, bson.errors.InvalidId):
        return JSONResponse(status_code=400,
                            content={"result": False, "message": "Bad Request", "detail": str(results)})
    if results.deleted_count == 0:
        return JSONResponse(status_code=404,
                            content={"result": True,
                                     "message": "not found",
                                     "detail": "no meeting found with id {}".format(meeting_id)})
    return JSONResponse(status_code=200,
                        content={"result": True,
                                 "message": "deleted {} meetings".format(results.deleted_count),
                                 "detail": None})


@router.get('/api/v1/meeting/{meeting_id}', tags=["meeting"])
async def get_one_meeting_by_meeting_id(meeting_id: str, details: bool = Query(False)):
    try:
        fields_to_hide = {"meeting_definition.Wertungen": 0, "meeting_definition.Wettkaempfe": 0, "results": 0,
                          "meeting_definition.Pflichtzeiten": 0, "created": 0, "updated": 0, "file_hash": 0}
        query = {"_id": ObjectId(meeting_id)}
        if details:
            fields_to_hide = None
        # results = mongo_handler.find_many_docs(col="meetings", query=query, fields_to_hide=fields_to_hide)
        results = mongo_handler.find_one_doc(col="meetings", query=query, fields_to_hide=fields_to_hide)
        return JSONResponse(status_code=200, content={"result": True,
                                                      "message": results,
                                                      "detail": None})
    except Exception as err:
        logger.error('Error in create_meeting() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})


@router.get('/api/v1/meeting/{meeting_id}/{swimmer_reg_id}', tags=["meeting"])
async def get_swimmer_results_for_one_meeting(meeting_id: str, swimmer_reg_id: str):
    try:
        query = {"_id": ObjectId(meeting_id)}
        results = mongo_handler.find_many_docs(col="meetings", query=query)
        if results is not None:
            results = results[0]["results"]["meeting_results"][swimmer_reg_id]
        return JSONResponse(status_code=200, content={"result": True,
                                                      "message": results,
                                                      "detail": None})
    except Exception as err:
        logger.error('Error in create_meeting() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})


@router.get('/api/v1/meeting/', tags=["meeting"])
async def get_all_meetings(date: Optional[str] = Query(None),
                           name: Optional[str] = Query(None),
                           detailed: bool = Query(False)):
    """

    """
    try:
        query = {}
        fields_to_hide = {"meeting_definition.Wertungen": 0, "meeting_definition.Wettkaempfe": 0, "results": 0,
                          "meeting_definition.Pflichtzeiten": 0, "created": 0, "updated": 0, "file_hash": 0}
        if date:
            query["meeting_definition.Abschnitte.abschnitts_datum"] = date
        if name:
            query["meeting_definition.Abschnitte.abschnitts_datum"] = name
        if detailed:
            fields_to_hide = None
        meetings = mongo_handler.find_many_docs(col="meetings", query=query, fields_to_hide=fields_to_hide)
        return JSONResponse(status_code=200, content={"result": True,
                                                      "message": meetings,
                                                      "detail": "Found {} meeting(s)".format(len(meetings))})
    except Exception as err:
        logger.error('Error in create_meeting() err: {}'.format(err))
        return JSONResponse(status_code=500, content={"result": False, "message": "internal error", "detail": str(err)})
