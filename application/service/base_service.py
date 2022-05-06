from typing import Type, Union, List
from pydantic import BaseModel
from pyee.asyncio import AsyncIOEventEmitter
from tortoise.exceptions import IntegrityError
from tortoise.transactions import atomic

from core.communication.publisher import Publisher
from core.dto.access import EntityId
from core.utils.error_format import integrity_error_format
from infrastructure.database.layer import DbLayer
from infrastructure.database.models import AbstractBaseModel
from infrastructure.database.repository import EntityRepository


class BaseService(Publisher):
    persistence: DbLayer
    target_model: Type[AbstractBaseModel]

    def __init__(self, persistence: DbLayer, emitter: AsyncIOEventEmitter):
        super().__init__(emitter)
        self.persistence = persistence

    @atomic()
    async def create(self, system_user: EntityId, _dto: BaseModel, **kwargs) -> AbstractBaseModel:
        if hasattr(_dto, "name"):
            await EntityRepository.check_exist(self.target_model, name=_dto.name)
        entity_kwargs = {field: value for field, value in _dto.dict().items() if value}
        try:
            entity = await self.target_model.create(**entity_kwargs)
        except IntegrityError as exception:
            integrity_error_format(exception)
        return entity

    async def read(self, _id: EntityId) -> AbstractBaseModel:
        related_fields = await DbLayer.extract_relatable_fields(self.target_model)
        return await self.target_model.get_or_none(id=_id).prefetch_related(*related_fields)

    async def read_all(self,
                       limit: int = None,
                       offset: int = None) -> Union[List[AbstractBaseModel],
                                                    AbstractBaseModel]:
        related_fields = await DbLayer.extract_relatable_fields(self.target_model)
        query = self.target_model.all().prefetch_related(*related_fields)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return await query
