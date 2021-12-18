from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum


class JsonResponseContent(BaseModel):
    result: bool
    message: str
    detail: str
