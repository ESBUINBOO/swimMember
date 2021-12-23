from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum


class Role(BaseModel):
    """
    data class for a keycloak role
    """
    attributes: Optional[Dict]
    clientRole: Optional[bool]
    composite: Optional[bool]
    description: Optional[str]
    name: Optional[str]
