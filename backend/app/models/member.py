from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum


class JsonResponseContent(BaseModel):
    result: bool
    message: str
    detail: str


class Roles(BaseModel):
    name: str
    description: Optional[str]
    clientRole: bool
    attributes: Optional[Dict]


class Address(BaseModel):
    street: str
    house_number: str
    zipcode: int
    town: str


class Member(BaseModel):
    # todo: EMailStr zum Laufen bekommen
    firstname: str
    lastname: str
    birth: str  # should be Datetime
    gender: str
    address: Address
    emails: List[str]
    mobile_phone_number: str
    phone_numbers: Optional[List[str]] = None
    member_since: Optional[str] = None
    role: str  # this should be str, because the roles are not static, so an ENUM doesnt make sense
