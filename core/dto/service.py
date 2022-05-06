from pydantic import BaseModel, Json, conlist
from typing import Optional

from core.dto.access import EntityId


class EmailStruct(BaseModel):
    """Schema for sending emails through Celery"""
    email: conlist(item_type=str, min_items=1)
    text: conlist(item_type=str, min_items=1)
    subject: str


class Auth:
    class LoginDto(BaseModel):
        username: str
        password: str


class ClaimDto:
    class CreationDto(BaseModel):
        pass_type: str
        claim_way: Optional[EntityId]
        pass_id: Optional[EntityId]
        approved: Optional[bool]
        is_in_blacklist: Optional[bool]
        pnd_agreement: Optional[bool]
        information: Optional[str]
        status: str

    class UpdateDto(BaseModel):
        pass_type: Optional[str]
        claim_way: Optional[EntityId]
        pass_id: Optional[EntityId]
        approved: Optional[bool]
        is_in_blacklist: Optional[bool]
        pnd_agreement: Optional[bool]
        information: Optional[str]
        status: Optional[str]


class VisitorDto:
    class CreationDto(BaseModel):
        first_name: str
        last_name: str
        middle_name: Optional[str]
        who_invited: Optional[str]
        destination: Optional[str]
        passport: Optional[EntityId]
        pass_id: Optional[EntityId]
        drive_license: Optional[EntityId]
        visitor_foto: Optional[EntityId]
        transport: Optional[EntityId]
        military_id: Optional[EntityId]
        claim: Optional[EntityId]

    class UpdateDto(BaseModel):
        first_name: Optional[str]
        last_name: Optional[str]
        middle_name: Optional[str]
        who_invited: Optional[str]
        destination: Optional[str]
        passport: Optional[EntityId]
        pass_id: Optional[EntityId]
        drive_license: Optional[EntityId]
        visitor_foto: Optional[EntityId]
        transport: Optional[EntityId]
        military_id: Optional[EntityId]
        claim: Optional[EntityId]


class VisitSessionDto:
    class CreationDto(BaseModel):
        visitor: EntityId
        enter: Optional[str]
        exit: Optional[str]

    class UpdateDto(BaseModel):
        enter: Optional[str]
        exit: Optional[str]


class PassportDto:
    class CreationDto(BaseModel):
        number: int
        division_code: Optional[str]
        registration: Optional[str]
        date_of_birth: Optional[str]
        place_of_birth: Optional[str]
        gender: Optional[str]

    class UpdateDto(BaseModel):
        number: Optional[int]
        division_code: Optional[str]
        registration: Optional[str]
        date_of_birth: Optional[str]
        place_of_birth: Optional[str]
        gender: Optional[str]


class DriveLicenseDto:
    class CreationDto(BaseModel):
        date_of_issue: Optional[str]
        expiration_date: Optional[str]
        place_of_issue: Optional[str]
        address_of_issue: Optional[str]
        number: int
        categories: Optional[str]

    class UpdateDto(BaseModel):
        date_of_issue: Optional[str]
        expiration_date: Optional[str]
        place_of_issue: Optional[str]
        address_of_issue: Optional[str]
        number: Optional[int]
        categories: Optional[str]


class VisitorFotoDto:
    # TODO !How to store foto!
    class CreationDto(BaseModel):
        signature: Optional[Json]
        webcam_img: Optional[str]
        scan_img: Optional[str]
        car_number_img: Optional[str]

    class UpdateDto(BaseModel):
        signature: Optional[Json]
        webcam_img: Optional[str]
        scan_img: Optional[str]
        car_number_img: Optional[str]


class MilitaryIdDto:
    class CreationDto(BaseModel):
        number: str
        date_of_birth: Optional[str]
        place_of_issue: Optional[str]
        date_of_issue: Optional[str]
        place_of_birth: Optional[str]

    class UpdateDto(BaseModel):
        number: Optional[str]
        date_of_birth: Optional[str]
        place_of_issue: Optional[str]
        date_of_issue: Optional[str]
        place_of_birth: Optional[str]


class PassDto:
    class CreationDto(BaseModel):
        rfid: Optional[int]
        pass_type: str
        valid_till: str
        valid: Optional[bool]

    class UpdateDto(BaseModel):
        rfid: Optional[int]
        pass_type: str
        valid_till: Optional[str]
        valid: Optional[bool]


class TransportDto:
    class CreationDto(BaseModel):
        model: Optional[str]
        number: str
        color: Optional[str]
        claims: conlist(item_type=EntityId, min_items=1)
        parking_places: Optional[EntityId]

    class UpdateDto(BaseModel):
        model: Optional[str]
        number: Optional[str]
        color: Optional[str]
        claims: Optional[conlist(item_type=EntityId, min_items=1)]
        parking_places: Optional[EntityId]


class BlackListDto:
    class CreationDto(BaseModel):
        visitor: EntityId
        level: Optional[str]

    class UpdateDto(BaseModel):
        visitor: Optional[EntityId]
        level: Optional[str]
