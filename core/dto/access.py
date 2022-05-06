from typing import Optional

from pydantic import BaseModel, conlist, Json, conint, IPvAnyAddress, EmailStr

EntityId = int
EntityName = str


class SystemUser:
    class CreationDto(BaseModel):
        first_name: str
        last_name: str
        middle_name: Optional[str]
        username: str
        password: str
        phone: Optional[str]
        email: Optional[EmailStr]
        scopes: conlist(item_type=EntityId, min_items=1)
        expire_session_delta: Optional[int]

    class UpdateDto(BaseModel):
        username: Optional[str]
        password: Optional[str]
        first_name: Optional[str]
        last_name: Optional[str]
        middle_name: Optional[str]
        phone: Optional[str]
        email: Optional[EmailStr]
        scopes: Optional[conlist(item_type=EntityId, min_items=1)]
        expire_session_delta: Optional[int]


class Zone:
    class CreationDto(BaseModel):
        name: str

    class UpdateDto(BaseModel):
        name: str


class ClaimWay:
    class CreationDto(BaseModel):
        system_users: conlist(item_type=int, min_items=1)
        roles: conlist(item_type=EntityId, min_items=1)

    class UpdateDto(BaseModel):
        system_users: Optional[conlist(item_type=int, min_items=1)]
        roles: Optional[conlist(item_type=EntityId, min_items=1)]


class ClaimToZone:
    class CreationDto(BaseModel):
        claim: EntityId
        zones: conlist(item_type=EntityId, min_items=1)
        pass_id: Optional[EntityId]

    class UpdateDto(BaseModel):
        claim: Optional[EntityId]
        zones: Optional[conlist(item_type=EntityId, min_items=1)]
        pass_id: Optional[EntityId]


class ParkingPlace:
    class CreationDto(BaseModel):
        enable: Optional[bool]
        real_number: int
        acquire_parking_intervals: Optional[EntityId]

    class UpdateDto(BaseModel):
        enable: Optional[bool]
        real_number: Optional[int]
        acquire_parking_intervals: Optional[EntityId]


class Parking:
    class CreationDto(BaseModel):
        max_places: int
        current_places: Optional[int]
        time_slot_interval: Optional[int]
        parking_places: Optional[EntityId]

    class UpdateDto(BaseModel):
        max_places: Optional[int]
        current_places: Optional[int]
        time_slot_interval: Optional[int]
        parking_places: Optional[EntityId]


class Role:
    class CreationDto(BaseModel):
        name: str

    class UpdateDto(BaseModel):
        name: str
