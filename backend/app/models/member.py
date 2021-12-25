from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from enum import Enum


class Address(BaseModel):
    street: str
    house_number: str
    zipcode: int
    town: str


class Gender(str, Enum):
    male = "Male"
    female = "Female"
    divers = "Divers"


class PhoneNumberTypes(str, Enum):
    mobile = "mobile"


class Member(BaseModel):
    firstname: str
    lastname: str
    birth: str  # should be Datetime
    gender: Gender
    address: Address
    emails: List[EmailStr]
    phone_numbers: Dict[PhoneNumberTypes, str]
    member_since: Optional[int]
    role: str


class Swimmer(Member):
    """
    reg_id: DSV Register ID
    active: state of the swimmer (active / inactive)
    fetch_results: fetch results from the dsv website
    parents: list of member ids of parents
    license: dsv license for the running year
    license_paid: is the dsv license paid for the running year
    medical_certificate: does it exist for the running year
    group: in which group is the swimmer
    role: must be something like 'swimmer'
    """
    # todo: reference to members (as parents)
    # todo: cluster members and swimmers to family
    reg_id: int
    active: bool
    fetch_results: bool = True
    parents: Optional[List[str]] = None
    license: Optional[int] = None
    license_paid: Optional[bool] = None
    medical_certificate: Optional[bool] = None
    group: str
    role = "swimmer"


class Coach(Member):
    coaching_license: str  # i.e. C, B, A, etc...
    license_valid_to: str  # datetime
    groups: Optional[List]
