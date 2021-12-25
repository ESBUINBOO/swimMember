from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum


class MemberCategories(Enum):
    member = "Member"
    swimmer = "Swimmer"
    coach = "Coach"
