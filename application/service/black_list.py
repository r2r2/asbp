from tortoise.transactions import atomic

import settings
from core.dto.access import EntityId
from core.dto.service import BlackListDto, EmailStruct
from core.communication.event import NotifyVisitorInBlackListEvent
from infrastructure.database.models import BlackList, AbstractBaseModel, Visitor, SystemUser
from application.exceptions import InconsistencyError
from application.service.base_service import BaseService


class BlackListService(BaseService):
    target_model = BlackList

    @staticmethod
    async def collect_target_users(visitor: Visitor) -> EmailStruct:

        security_officers = await SystemUser.filter(scopes=5)  # Role.get(id=5) == 'security_officer'

        emails = list()
        texts = list()
        for user in security_officers:
            text = f"Hello, {user.first_name.title()}!\n " \
                   f"{settings.BLACKLIST_NOTIFICATION_BODY_TEXT} " \
                   f"ID={visitor.id}: {visitor.first_name} {visitor.last_name}"
            emails.append(user.email)
            texts.append(text)

        email_struct = EmailStruct(email=emails,
                                   text=texts,
                                   subject=settings.BLACKLIST_NOTIFICATION_SUBJECT_TEXT)

        return email_struct

    @atomic()
    async def create(self, system_user: EntityId, dto: BlackListDto.CreationDto) -> AbstractBaseModel:
        visitor = await Visitor.get_or_none(id=dto.visitor)
        if visitor is None:
            raise InconsistencyError(message=f"Visitor with id={dto.visitor} does not exist."
                                             "You should provide valid Visitor for BlackList")

        black_list = await BlackList.create(visitor=visitor,
                                            level=dto.level)

        self.notify(NotifyVisitorInBlackListEvent(await self.collect_target_users(visitor)))

        return black_list

    @atomic()
    async def update(self, system_user: EntityId, entity_id: EntityId, dto: BlackListDto.UpdateDto) -> BlackList:
        black_list = await BlackList.get_or_none(id=entity_id).prefetch_related('visitor')
        if black_list is None:
            raise InconsistencyError(message=f"BlackList with id={entity_id} does not exist.")

        visitor = None
        if dto.visitor:
            visitor = await Visitor.get_or_none(id=dto.visitor)

        black_list.visitor = visitor or black_list.visitor
        black_list.level = dto.level or black_list.level

        await black_list.save()
        self.notify(NotifyVisitorInBlackListEvent(await self.collect_target_users(visitor)))

        return black_list

    @atomic()
    async def delete(self, system_user: EntityId, entity_id: EntityId) -> EntityId:
        black_list = await BlackList.get_or_none(id=entity_id).prefetch_related("visitor")
        if black_list is None:
            raise InconsistencyError(message=f"BlackList with id={entity_id} does not exist.")

        visitor = black_list.visitor
        self.notify(NotifyVisitorInBlackListEvent(await self.collect_target_users(visitor)))

        await black_list.delete()
        return entity_id
