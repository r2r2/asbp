from typing import Union, List, Optional
from pydantic import BaseModel
from sanic import Request

from sanic.exceptions import NotFound
from sanic.response import HTTPResponse, json
from sanic.views import HTTPMethodView

from application.service.black_list import BlackListService
from core.dto import validate
from core.dto.access import EntityId
from core.dto.service import (ClaimDto,
                              VisitorDto,
                              PassportDto,
                              MilitaryIdDto,
                              VisitSessionDto,
                              DriveLicenseDto,
                              PassDto,
                              TransportDto,
                              BlackListDto)
from infrastructure.database.models import (AbstractBaseModel,
                                            SystemUser,
                                            Claim,
                                            Visitor,
                                            Passport,
                                            MilitaryId,
                                            VisitSession,
                                            DriveLicense,
                                            Pass,
                                            Transport,
                                            BlackList)

from application.service.base_service import BaseService
from application.service.claim import ClaimService
from application.service.visitor import (VisitorService,
                                         PassportService,
                                         MilitaryIdService,
                                         VisitSessionService,
                                         DriveLicenseService,
                                         PassService,
                                         TransportService)
from core.server.auth import protect


class BaseServiceController(HTTPMethodView):
    enabled_scopes: Union[List[str], str]
    target_route: str
    target_service: BaseService
    returned_model: AbstractBaseModel
    post_dto: BaseModel
    put_dto: BaseModel

    @staticmethod
    def validate(dto_type: BaseModel, request: Request) -> BaseModel:
        return validate(dto_type, request)

    @protect(retrive_user=False)
    async def get(self, request: Request, entity_id: Optional[EntityId] = None) -> HTTPResponse:
        if entity_id is None:
            limit = request.args.get("limit")
            offset = request.args.get("offset")
            limit = int(limit) if limit and limit.isdigit() else None
            offset = int(offset) if offset and offset.isdigit() else None
            models = await request.app.ctx.service_registry.get(self.target_service).read_all(limit, offset)
            return json([await model.values_dict() for model in models])

        model = await request.app.ctx.service_registry.get(self.target_service).read(entity_id)
        if model:
            return json(await model.values_dict())
        else:
            raise NotFound()

    @protect()
    async def post(self, request: Request, system_user: SystemUser) -> HTTPResponse:
        dto = self.validate(self.post_dto, request)
        service_name: BaseServiceController.target_service = request.app.ctx.service_registry.get(self.target_service)
        model = await service_name.create(system_user, dto)
        return json(await model.values_dict())

    @protect()
    async def put(self, request: Request, system_user: SystemUser, entity_id: EntityId) -> HTTPResponse:
        dto = self.validate(self.put_dto, request)
        service_name: BaseServiceController.target_service = request.app.ctx.service_registry.get(self.target_service)
        model = await service_name.update(system_user, entity_id, dto)
        return json(await model.values_dict())

    @protect()
    async def delete(self, request: Request, system_user: SystemUser, entity_id: EntityId) -> HTTPResponse:
        service_name: BaseServiceController.target_service = request.app.ctx.service_registry.get(self.target_service)
        model = await service_name.delete(system_user, entity_id)
        return json(model)

    @protect()
    async def patch(self, request: Request, system_user: SystemUser, entity_id: EntityId) -> HTTPResponse:
        return await self.put(request, system_user, entity_id)


class ClaimController:
    returned_model = Claim

    class Create(BaseServiceController):
        enabled_scopes = ["root", "admin"]
        target_route = "/claims"
        target_service = ClaimService
        post_dto = ClaimDto.CreationDto

    class Update(BaseServiceController):
        enabled_scopes = ["root", "admin"]
        target_route = "/claims/<entity_id:int>"
        target_service = ClaimService
        put_dto = ClaimDto.UpdateDto


class VisitorController:
    returned_model = Visitor

    class Create(BaseServiceController):
        enabled_scopes = ["root", "admin"]
        target_route = "/visitors"
        post_dto = VisitorDto.CreationDto
        target_service = VisitorService

    class Update(BaseServiceController):
        enabled_scopes = ["root", "admin"]
        target_route = "/visitors/<entity_id:int>"
        put_dto = VisitorDto.UpdateDto
        target_service = VisitorService


class PassportController:
    returned_model = Passport

    class Create(BaseServiceController):
        target_route = "/passports"
        enabled_scopes = ["root", "admin"]
        target_service = PassportService
        post_dto = PassportDto.CreationDto

    class Update(BaseServiceController):
        target_route = "/passports/<entity_id:int>"
        enabled_scopes = ["root", "admin"]
        target_service = PassportService
        put_dto = PassportDto.UpdateDto


class MilitaryIdController:
    returned_model = MilitaryId

    class Create(BaseServiceController):
        target_route = "/militaryids"
        enabled_scopes = ["root", "admin"]
        target_service = MilitaryIdService
        post_dto = MilitaryIdDto.CreationDto

    class Update(BaseServiceController):
        target_route = "/militaryids/<entity_id:int>"
        enabled_scopes = ["root", "admin"]
        target_service = MilitaryIdService
        put_dto = MilitaryIdDto.UpdateDto


class VisitSessionController:
    returned_model = VisitSession

    class Create(BaseServiceController):
        target_route = "/visitsessions"
        enabled_scopes = ["root", "admin"]
        target_service = VisitSessionService
        post_dto = VisitSessionDto.CreationDto

    class Update(BaseServiceController):
        target_route = "/visitsessions/<entity_id:int>"
        enabled_scopes = ["root", "admin"]
        target_service = VisitSessionService
        put_dto = VisitSessionDto.UpdateDto


class DriveLicenseController:
    returned_model = DriveLicense

    class Create(BaseServiceController):
        target_route = "/drivelicenses"
        enabled_scopes = ["root", "admin"]
        target_service = DriveLicenseService
        post_dto = DriveLicenseDto.CreationDto

    class Update(BaseServiceController):
        target_route = "/drivelicenses/<entity_id:int>"
        enabled_scopes = ["root", "admin"]
        target_service = DriveLicenseService
        put_dto = DriveLicenseDto.UpdateDto


class PassController:
    returned_model = Pass

    class Create(BaseServiceController):
        target_route = "/passes"
        enabled_scopes = ["root", "admin"]
        target_service = PassService
        post_dto = PassDto.CreationDto

    class Update(BaseServiceController):
        target_route = "/passes/<entity_id:int>"
        enabled_scopes = ["root", "admin"]
        target_service = PassService
        put_dto = PassDto.UpdateDto


class TransportController:
    returned_model = Transport

    class Create(BaseServiceController):
        target_route = "/transports"
        enabled_scopes = ["root", "admin"]
        target_service = TransportService
        post_dto = TransportDto.CreationDto

    class Update(BaseServiceController):
        target_route = "/transports/<entity_id:int>"
        enabled_scopes = ["root", "admin"]
        target_service = TransportService
        put_dto = TransportDto.UpdateDto


class BlackListController:
    returned_model = BlackList

    class Create(BaseServiceController):
        target_route = "/blacklist"
        enabled_scopes = ["root", "admin"]
        target_service = BlackListService
        post_dto = BlackListDto.CreationDto

    class Update(BaseServiceController):
        target_route = "/blacklist/<entity_id:int>"
        enabled_scopes = ["root", "admin"]
        target_service = BlackListService
        put_dto = BlackListDto.UpdateDto
