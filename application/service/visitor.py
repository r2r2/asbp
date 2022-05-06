from datetime import datetime
from typing import Union
from tortoise import exceptions
from tortoise.transactions import atomic

import settings
from core.communication.event import NotifyVisitorInBlackListEvent
from core.dto.access import EntityId
from core.dto.service import (VisitorDto,
                              PassportDto,
                              MilitaryIdDto,
                              VisitSessionDto,
                              DriveLicenseDto,
                              PassDto,
                              TransportDto)
from infrastructure.database.repository import EntityRepository
from infrastructure.database.models import (Passport,
                                            Pass,
                                            DriveLicense,
                                            MilitaryId,
                                            Transport,
                                            SystemUser,
                                            Visitor,
                                            AbstractBaseModel,
                                            VisitSession,
                                            VisitorFoto,
                                            ParkingPlace,
                                            Claim,
                                            BlackList)
from application.exceptions import InconsistencyError
from application.service.base_service import BaseService
from application.service.black_list import BlackListService
from core.plugins.plugins_wrap import AddPlugins


class VisitorService(BaseService):
    target_model = Visitor

    @atomic()
    async def get_visitor_documents(self, dto: Union[VisitorDto.CreationDto,
                                                     VisitorDto.UpdateDto]) -> dict:
        """Trying to get Visitor's documents, transports, claims and returning them as a dict"""
        documents = {
            "passport": await Passport.get_or_none(id=dto.passport) if dto.passport else None,
            "pass_id": await Pass.get_or_none(id=dto.pass_id) if dto.pass_id else None,
            "drive_license": await DriveLicense.get_or_none(id=dto.drive_license) if dto.drive_license else None,
            "military_id": await MilitaryId.get_or_none(id=dto.military_id) if dto.military_id else None,
            "transport": await Transport.get_or_none(id=dto.transport) if dto.transport else None,
            "claim": await Claim.get_or_none(id=dto.claim) if dto.claim else None,
        }
        return documents

    @atomic()
    async def create(self, system_user: SystemUser, dto: VisitorDto.CreationDto) -> Visitor:
        try:
            documents = await self.get_visitor_documents(dto)

            visitor = await Visitor.create(first_name=dto.first_name,
                                           last_name=dto.last_name,
                                           middle_name=dto.middle_name,
                                           who_invited=dto.who_invited,
                                           destination=dto.destination,
                                           passport=documents["passport"],
                                           pass_id=documents["pass_id"],
                                           drive_license=documents["drive_license"],
                                           military_id=documents["military_id"],
                                           transport=documents["transport"],
                                           claim=documents["claim"])
            # TODO visitor_foto

            visitor_in_black_list = await BlackList.exists(visitor=visitor)
            if visitor_in_black_list:
                self.notify(NotifyVisitorInBlackListEvent(await BlackListService.collect_target_users(visitor)))

            return visitor

        except exceptions.IntegrityError as ex:
            raise InconsistencyError(message=f"{ex}.")

    @atomic()
    async def update(self, system_user: SystemUser, entity_id: EntityId, dto: VisitorDto.UpdateDto) -> Visitor:
        visitor = await Visitor.get_or_none(id=entity_id)
        if visitor is None:
            raise InconsistencyError(message=f"Visitor with id={entity_id} does not exist.")

        visitor_in_black_list = await BlackList.exists(visitor=visitor)
        if visitor_in_black_list:
            self.notify(NotifyVisitorInBlackListEvent(await BlackListService.collect_target_users(visitor)))

        documents = await self.get_visitor_documents(dto)

        try:
            if documents["pass_id"]:
                if visitor_in_black_list:
                    raise InconsistencyError(message=f"Visitor with id={entity_id} is in BlackList")
                else:
                    visitor.pass_id = documents["pass_id"] or visitor.pass_id

            visitor.first_name = dto.first_name or visitor.first_name
            visitor.last_name = dto.last_name or visitor.last_name
            visitor.middle_name = dto.middle_name or visitor.middle_name
            visitor.who_invited = dto.who_invited or visitor.who_invited
            visitor.destination = dto.destination or visitor.destination
            visitor.passport = documents["passport"] or visitor.passport
            visitor.drive_license = documents["drive_license"] or visitor.drive_license
            visitor.military_id = documents["military_id"] or visitor.military_id
            visitor.transport = documents["transport"] or visitor.transport
            visitor.claim = documents["claim"] or visitor.claim
            # TODO visitor_foto
            await visitor.save()
            return visitor

        except exceptions.IntegrityError as ex:
            raise InconsistencyError(message=f"{ex}")

    @atomic()
    async def delete(self, system_user: SystemUser, entity_id: EntityId) -> EntityId:
        await EntityRepository.check_not_exist_or_delete(Visitor, entity_id)
        await Visitor.filter(id=entity_id).update(deleted=True)
        return entity_id


class PassportService(BaseService):
    target_model = Passport

    @atomic()
    async def create(self, system_user: SystemUser, dto: PassportDto.CreationDto) -> AbstractBaseModel:
        return await super().create(system_user.id, dto)

    @atomic()
    async def update(self, system_user: SystemUser, entity_id: EntityId, dto: PassportDto.UpdateDto) -> Passport:
        passport = await Passport.get_or_none(id=entity_id)
        if passport is None:
            raise InconsistencyError(message=f"Passport with id={entity_id} does not exist.")

        for field, value in dto.dict().items():
            if value and (field == "date_of_birth"):
                passport.date_of_birth = datetime.strptime(dto.date_of_birth, settings.ACCESS_DATE_FORMAT)

            if value and (field != "date_of_birth"):
                setattr(passport, field, value)

        await passport.save()
        return passport

    @atomic()
    async def delete(self, system_user: SystemUser, entity_id: EntityId) -> EntityId:
        passport = await Passport.get_or_none(id=entity_id)
        if passport is None:
            raise InconsistencyError(message=f"Passport with id={entity_id} does not exist.")
        await passport.delete()
        return entity_id


class MilitaryIdService(BaseService):
    target_model = MilitaryId

    @atomic()
    async def create(self, system_user: SystemUser, dto: MilitaryIdDto.CreationDto) -> AbstractBaseModel:
        return await super().create(system_user.id, dto)

    @atomic()
    async def update(self, system_user: SystemUser, entity_id: EntityId, dto: MilitaryIdDto.UpdateDto) -> MilitaryId:
        military_id = await MilitaryId.get_or_none(id=entity_id)
        if military_id is None:
            raise InconsistencyError(message=f"MilitaryId with id={entity_id} does not exist.")

        for field, value in dto.dict().items():
            if value and (field == "date_of_birth"):
                military_id.date_of_birth = datetime.strptime(dto.date_of_birth, settings.ACCESS_DATE_FORMAT)

            elif value and (field == "date_of_issue"):
                military_id.date_of_issue = datetime.strptime(dto.date_of_issue, settings.ACCESS_DATE_FORMAT)

            elif value and (field != "date_of_birth") and (field != "date_of_issue"):
                setattr(military_id, field, value)

        await military_id.save()
        return military_id

    @atomic()
    async def delete(self, system_user: SystemUser, entity_id: EntityId) -> EntityId:
        military_id = await MilitaryId.get_or_none(id=entity_id)
        if military_id is None:
            raise InconsistencyError(message=f"MilitaryId with id={entity_id} does not exist.")
        await military_id.delete()
        return entity_id


class VisitSessionService(BaseService):
    target_model = VisitSession

    @atomic()
    async def create(self, system_user: SystemUser, dto: VisitSessionDto.CreationDto) -> VisitSession:

        visitor = await Visitor.get_or_none(id=dto.visitor)
        if visitor is None:
            raise InconsistencyError(message=f"There is no visitor with id={dto.visitor}. "
                                             f"You should provide valid Visitor for VisitSession.")

        visit_session = await VisitSession.create(enter=dto.enter,
                                                  exit=dto.exit,
                                                  visitor=visitor)
        return visit_session

    @atomic()
    async def update(self, system_user: SystemUser, entity_id: EntityId, dto: VisitSessionDto.UpdateDto) -> VisitSession:
        visit_session = await VisitSession.get_or_none(id=entity_id)
        if visit_session is None:
            raise InconsistencyError(message=f"VisitSession with id={entity_id} does not exist.")

        enter_time = exit_time = None
        if dto.enter:
            enter_time = datetime.strptime(dto.enter, settings.ACCESS_DATETIME_FORMAT)

        if dto.exit:
            exit_time = datetime.strptime(dto.exit, settings.ACCESS_DATETIME_FORMAT)

        visit_session.enter = enter_time or visit_session.enter
        visit_session.exit = exit_time or visit_session.exit

        await visit_session.save()
        return visit_session

    @atomic()
    async def delete(self, system_user: SystemUser, entity_id: EntityId) -> EntityId:
        visit_session = await VisitSession.get_or_none(id=entity_id)
        if visit_session is None:
            raise InconsistencyError(message=f"VisitSession with id={entity_id} does not exist.")
        await visit_session.delete()
        return entity_id


class DriveLicenseService(BaseService):
    target_model = DriveLicense

    @atomic()
    async def create(self, system_user: EntityId, dto: DriveLicenseDto.CreationDto) -> AbstractBaseModel:
        return await super().create(system_user, dto)

    @atomic()
    async def update(self, system_user: SystemUser, entity_id: EntityId, dto: DriveLicenseDto.UpdateDto) -> DriveLicense:
        drive_license = await DriveLicense.get_or_none(id=entity_id)
        if drive_license is None:
            raise InconsistencyError(message=f"DriveLicense with id={entity_id} does not exist.")

        for field, value in dto.dict().items():
            if value and (field == "date_of_issue"):
                drive_license.date_of_issue = datetime.strptime(dto.date_of_issue, settings.ACCESS_DATE_FORMAT)

            elif value and (field == "expiration_date"):
                drive_license.expiration_date = datetime.strptime(dto.expiration_date, settings.ACCESS_DATE_FORMAT)

            elif value and (field != "date_of_issue") and (field != "expiration_date"):
                setattr(drive_license, field, value)

        await drive_license.save()
        return drive_license

    @atomic()
    async def delete(self, system_user: SystemUser, entity_id: EntityId) -> EntityId:
        drive_license = await DriveLicense.get_or_none(id=entity_id)
        if drive_license is None:
            raise InconsistencyError(message=f"DriveLicense with id={entity_id} does not exist.")
        await drive_license.delete()
        return entity_id


class VisitorFotoService(BaseService):
    target_model = VisitorFoto

    # TODO !How to store foto!


class PassService(BaseService):
    target_model = Pass

    @atomic()
    async def create(self, system_user: EntityId, dto: PassDto.CreationDto) -> AbstractBaseModel:
        valid_till = datetime.strptime(dto.valid_till, settings.ACCESS_DATETIME_FORMAT)

        visitor_pass = await Pass.create(rfid=dto.rfid,
                                         pass_type=dto.pass_type,
                                         valid_till=valid_till)
        return visitor_pass

    @atomic()
    async def update(self, system_user: EntityId, entity_id: EntityId, dto: PassDto.UpdateDto) -> Pass:
        visitor_pass = await Pass.get_or_none(id=entity_id)
        if visitor_pass is None:
            raise InconsistencyError(message=f"Pass with id={entity_id} does not exist.")

        for field, value in dto.dict().items():
            if value and (field == "valid_till"):
                visitor_pass.valid_till = datetime.strptime(dto.valid_till, settings.ACCESS_DATETIME_FORMAT)

            elif value and (field != "valid_till"):
                visitor_pass.valid = False if dto.valid is False else True

                setattr(visitor_pass, field, value)

        await visitor_pass.save()
        return visitor_pass

    @atomic()
    async def delete(self, system_user: EntityId, entity_id: EntityId) -> EntityId:
        visitor_pass = await Pass.get_or_none(id=entity_id)
        if visitor_pass is None:
            raise InconsistencyError(message=f"Pass with id={entity_id} does not exist.")
        await visitor_pass.delete()
        return entity_id


class TransportService(BaseService):
    target_model = Transport

    @atomic()
    async def create(self, system_user: EntityId, dto: TransportDto.CreationDto) -> Transport:
        await EntityRepository.check_exist(Transport, number=dto.number)

        parking_place = await ParkingPlace.get_or_none(id=dto.parking_places)

        transport = await Transport.create(model=dto.model,
                                           number=dto.number.upper(),
                                           color=dto.color,
                                           parking_places=parking_place)
        claims = await Claim.filter(id__in=dto.claims)
        for claim in claims:
            await transport.claims.add(claim)

        return transport

    @atomic()
    async def update(self, system_user: EntityId, entity_id: EntityId, dto: TransportDto.UpdateDto) -> Transport:
        transport = await Transport.get_or_none(id=entity_id)
        if transport is None:
            raise InconsistencyError(message=f"Transport with id={entity_id} does not exist.")

        parking_place = None
        if dto.parking_places:
            parking_place = await ParkingPlace.get_or_none(id=dto.parking_places)

        transport.model = dto.model or transport.model
        transport.number = dto.number.upper() or transport.number
        transport.color = dto.color or transport.color
        transport.parking_places = parking_place or transport.parking_places

        if dto.claims:
            claims = await Claim.filter(id__in=dto.claims)
            for claim in claims:
                await transport.claims.add(claim)

        await transport.save()
        return transport

    @atomic()
    async def delete(self, system_user: EntityId, entity_id: EntityId) -> EntityId:
        transport = await Transport.get_or_none(id=entity_id)
        if transport is None:
            raise InconsistencyError(message=f"Transport with id={entity_id} does not exist.")
        await transport.delete()
        return entity_id
