from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from enum import Enum


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
    emails: List[EmailStr]  # List of E-Mail
    mobile_phone_number: str
    phone_numbers: Optional[List[str]] = None
    member_since: Optional[str] = None
    role: str  # this should be str, because the roles are not static, so an ENUM doesnt make sense
