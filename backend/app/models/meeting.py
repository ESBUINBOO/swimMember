from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum


class Timing(str, Enum):
    manual = "HANDZEIT"
    automatic = "AUTOMATISCH"
    semi_automatic = "HALBAUTOMATISCH"


class Organizer(BaseModel):
    club = str
    contact = str
    email = str


class Meeting(BaseModel):
    name: str
    date: list
    location: str
    course: str
    timing: Timing
    sections: list
    organizer: Organizer
