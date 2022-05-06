from typing import Optional, List, Type, Union
from pydantic import BaseModel
from sanic import Request
from sanic.exceptions import NotFound
from sanic.response import HTTPResponse, json
from sanic.views import HTTPMethodView

from application.access.access import (SystemUserAccess,
                                       ZoneAccess,
                                       ClaimWayAccess,
                                       ClaimToZoneAccess,
                                       ParkingPlaceAccess,
                                       ParkingAccess,
                                       RoleAccess)
from application.access.base_access import BaseAccess
from core.dto import validate, access
from core.dto.access import EntityId
from core.server.auth import protect


class BaseAccessController(HTTPMethodView):
    enabled_scopes: Union[List[str], str]
    entity_name: str
    identity_type: Type
    post_dto: BaseModel
    put_dto: BaseModel
    access_type: BaseAccess

    @staticmethod
    def validate(dto_type: BaseModel, request: Request) -> BaseModel:
        return validate(dto_type, request)

    @protect(retrive_user=False)
    async def get(self, request: Request, entity: Optional[EntityId] = None) -> HTTPResponse:
        if entity is None:
            limit = request.args.get("limit")
            offset = request.args.get("offset")
            limit = int(limit) if limit and limit.isdigit() else None
            offset = int(offset) if offset and offset.isdigit() else None
            models = await request.app.ctx.access_registry.get(self.access_type).read_all(limit, offset)
            return json([await model.values_dict() for model in models])

        model = await request.app.ctx.access_registry.get(self.access_type).read(entity)
        if model:
            return json(await model.values_dict())
        else:
            raise NotFound()

    @protect()
    async def post(self, request: Request, user: EntityId) -> HTTPResponse:
        dto = self.validate(self.post_dto, request)
        model = await request.app.ctx.access_registry.get(self.access_type).create(user, dto)
        return json(await model.values_dict())

    @protect()
    async def put(self, request: Request, user: EntityId, entity: EntityId = None) -> HTTPResponse:
        dto = self.validate(self.put_dto, request)
        return json(await request.app.ctx.access_registry.get(self.access_type).update(user, entity, dto))

    @protect()
    async def delete(self, request: Request, user: EntityId, entity: EntityId = None) -> HTTPResponse:
        return json(await request.app.ctx.access_registry.get(self.access_type).delete(user, entity))


class SystemUserController(BaseAccessController):
    entity_name = 'users'
    enabled_scopes = ["root", "admin"]
    identity_type = int
    post_dto = access.SystemUser.CreationDto
    put_dto = access.SystemUser.UpdateDto
    access_type = SystemUserAccess


class ZoneController(BaseAccessController):
    entity_name = 'zone'
    enabled_scopes = ["root", "admin"]
    identity_type = int
    post_dto = access.Zone.CreationDto
    put_dto = access.Zone.UpdateDto
    access_type = ZoneAccess


class ClaimWayController(BaseAccessController):
    entity_name = 'claimway'
    enabled_scopes = ["root", "admin"]
    identity_type = int
    post_dto = access.ClaimWay.CreationDto
    put_dto = access.ClaimWay.UpdateDto
    access_type = ClaimWayAccess


class ClaimToZoneController(BaseAccessController):
    entity_name = 'claimtozone'
    enabled_scopes = ["root", "admin"]
    identity_type = int
    post_dto = access.ClaimToZone.CreationDto
    put_dto = access.ClaimToZone.UpdateDto
    access_type = ClaimToZoneAccess


class ParkingPlaceController(BaseAccessController):
    entity_name = 'parkingplace'
    enabled_scopes = ["root", "admin"]
    identity_type = int
    post_dto = access.ParkingPlace.CreationDto
    put_dto = access.ParkingPlace.UpdateDto
    access_type = ParkingPlaceAccess


class ParkingController(BaseAccessController):
    entity_name = 'parking'
    enabled_scopes = ["root", "admin"]
    identity_type = int
    post_dto = access.Parking.CreationDto
    put_dto = access.Parking.UpdateDto
    access_type = ParkingAccess


class RoleController(BaseAccessController):
    entity_name = 'role'
    enabled_scopes = ["root", "admin"]
    identity_type = int
    post_dto = access.Role.CreationDto
    put_dto = access.Role.UpdateDto
    access_type = RoleAccess
