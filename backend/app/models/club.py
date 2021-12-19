from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum


# Clubs = KC Realms
# Groups = KC Groups
class Clubs(str, Enum):
    # todo: this is for mega admin only!
    w98 = "Wassersportfreunde von 1989"
    test = "test"
    contact_person: Optional[str] = None


class Groups(BaseModel):
    group_name: str
    club_name: Clubs
    coaches: Optional[list] = None
    members: Optional[list] = None
