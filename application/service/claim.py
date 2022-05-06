from tortoise.transactions import atomic

import settings
from infrastructure.database.models import (SystemUser,
                                            Claim,
                                            ClaimWay,
                                            Pass,
                                            AbstractBaseModel)
from application.exceptions import InconsistencyError
from application.service.base_service import BaseService
from core.dto.access import EntityId
from core.dto.service import ClaimDto, EmailStruct
from core.communication.event import NotifyUsersInClaimWayEvent
from core.plugins.plugins_wrap import AddPlugins


class ClaimService(BaseService):
    target_model = Claim

    @staticmethod
    async def _collect_target_users(claim_way: ClaimWay) -> EmailStruct:
        system_users = claim_way.__dict__.get('_system_users')

        emails = list()
        texts = list()
        for user in system_users:
            text = f"Hello, {user.first_name.title()}!\n " \
                   f"{settings.CLAIMWAY_BODY_TEXT}"

            emails.append(user.email)
            texts.append(text)

        email_struct = EmailStruct(email=emails,
                                   text=texts,
                                   subject=settings.CLAIMWAY_SUBJECT_TEXT)

        return email_struct

    @atomic()
    # @AddPlugins()
    async def create(self, system_user: SystemUser, dto: ClaimDto.CreationDto) -> Claim:
        """Place Claim for visiting by specified visitor"""
        pass_id = await Pass.get_or_none(id=dto.pass_id)
        claim_way = await ClaimWay.get_or_none(id=dto.claim_way).prefetch_related("system_users")

        claim = await Claim.create(pass_type=dto.pass_type,
                                   claim_way=claim_way,
                                   pass_id=pass_id,
                                   information=dto.information,
                                   status=dto.status)
        if claim_way is not None:
            self.notify(NotifyUsersInClaimWayEvent(await self._collect_target_users(claim_way)))

        return claim

    @atomic()
    async def update(self, system_user: SystemUser, entity_id: EntityId, dto: ClaimDto.UpdateDto) -> AbstractBaseModel:
        claim = await self.read(entity_id)
        if claim is None:
            raise InconsistencyError(message=f"Claim with id={entity_id} does not exist.")

        claim_way = await ClaimWay.get_or_none(id=dto.claim_way).prefetch_related("system_users")
        pass_id = await Pass.get_or_none(id=dto.pass_id)

        if dto.is_in_blacklist is not None:
            claim.is_in_blacklist = False if dto.is_in_blacklist is False else True

        if dto.pnd_agreement is not None:
            claim.pnd_agreement = False if dto.pnd_agreement is False else True

        if dto.approved is not None:
            claim.approved = False if dto.approved is False else True

        if pass_id is not None:
            if claim.approved:
                claim.pass_id = pass_id or claim.pass_id
            else:
                raise InconsistencyError(message=f"Claim id={entity_id} should be approved before assign Pass to it")

        claim.pass_type = dto.pass_type or claim.pass_type
        claim.claim_way = claim_way or claim.claim_way
        claim.information = dto.information or claim.information
        claim.status = dto.status or claim.status

        if dto.approved or dto.status:
            # If changing sensitive fields notify related users in ClaimWay
            if claim.claim_way is not None:
                claim_way = await ClaimWay.get_or_none(id=claim.claim_way).prefetch_related("system_users")
                self.notify(NotifyUsersInClaimWayEvent(await self._collect_target_users(claim_way)))

        if claim_way is not None:
            self.notify(NotifyUsersInClaimWayEvent(await self._collect_target_users(claim_way)))

        await claim.save()
        return claim

    @atomic()
    async def delete(self, system_user: SystemUser, entity_id: EntityId) -> EntityId:
        claim = await Claim.get_or_none(id=entity_id)
        if claim is None:
            raise InconsistencyError(message=f"Claim with id={entity_id} does not exist.")

        await claim.delete()
        return entity_id
