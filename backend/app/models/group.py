from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum


class Group(BaseModel):
    """
    data class for a keycloak group
    """
    id: Optional[str]
    attributes: Optional[Dict]
    access: Optional[Dict]
    clientRoles: Optional[Dict]
    realmRoles: Optional[List[str]]
    # path: Optional[str]
    name: Optional[str]
    # subGroups: Optional[List[Group]]


class Groups(Group):
    subGroups: Optional[List[Group]]
