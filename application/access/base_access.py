from typing import Union, Type, List
from pydantic import BaseModel
from tortoise.transactions import atomic
from tortoise.exceptions import IntegrityError

from infrastructure.database.models import AbstractBaseModel
from infrastructure.database.layer import DbLayer
from infrastructure.database.repository import EntityRepository
from core.utils.error_format import integrity_error_format
from core.dto.access import EntityId


class BaseAccess:
    __slots__ = 'target_model'
    target_model: Type[AbstractBaseModel]

    @atomic()
    async def create(self, alter_user: EntityId, _dto: BaseModel, **kwargs) -> AbstractBaseModel:
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

    @atomic()
    async def update(self, alter_user: EntityId, entity_id: EntityId, dto: BaseModel) -> EntityId:
        await EntityRepository.check_not_exist_or_delete(self.target_model, entity_id)
        entity = await DbLayer.get_optional_view(self.target_model, entity_id)
        for field, value in dto.dict().items():
            if value:
                setattr(entity, field, value)
        await entity.save()
        return entity_id

    @atomic()
    async def delete(self, alter_user: EntityId, entity_id: EntityId) -> EntityId:
        raise NotImplementedError()
