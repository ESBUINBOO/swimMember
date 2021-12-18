import os
import sys
import logging
import base64
from typing import Optional, List, Union
import uvicorn
from fastapi import FastAPI, Header, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from enum import Enum
sys.path.append("app")
from routers import members_and_roles, clubs_and_groups, swimmers, meetings
from internal import admin

logger = logging.getLogger('FAST_API_LOGGER')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

app = FastAPI()
app.include_router(members_and_roles.router)
app.include_router(clubs_and_groups.router)
app.include_router(swimmers.router)
app.include_router(meetings.router)
app.include_router(admin.router)


@app.get('/api/v1/health')
def health_check():
    # todo: check dependencies like in itsc app
    return JSONResponse(status_code=200,
                        content={"result": True,
                                 "message": "Hello World from fast api service",
                                 "detail": None})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3090)
