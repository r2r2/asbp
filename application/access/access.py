from typing import Union
from tortoise import exceptions
from tortoise.transactions import atomic

from infrastructure.database.models import (SystemUser,
                                            Role,
                                            Zone,
                                            AbstractBaseModel,
                                            ClaimWay,
                                            ClaimToZone,
                                            Claim,
                                            Pass,
                                            ParkingPlace,
                                            AcquireParkingInterval,
                                            Parking)

from application.access.base_access import BaseAccess
from core.dto import access
from core.dto.access import EntityId
from core.utils.crypto import BaseCrypto
from infrastructure.database.repository import EntityRepository
from application.exceptions import InconsistencyError


class SystemUserAccess(BaseAccess):
    target_model = SystemUser

    @atomic()
    async def create(self, alter_user: EntityId, dto: access.SystemUser.CreationDto) -> SystemUser:
        await EntityRepository.check_exist(SystemUser, username=dto.username)

        crypted_password, salt = BaseCrypto.encrypt_password(dto.password)

        try:
            system_user = await SystemUser.create(first_name=dto.first_name,
                                                  last_name=dto.last_name,
                                                  middle_name=dto.middle_name,
                                                  username=dto.username,
                                                  password=crypted_password,
                                                  salt=salt,
                                                  phone=dto.phone,
                                                  email=dto.email, )
            roles = await Role.filter(id__in=dto.scopes)
            for role in roles:
                await system_user.scopes.add(role)

            return system_user

        except exceptions.ValidationError as ex:
            raise InconsistencyError(message=f"There is validation problem with {ex}.")
        except Exception as exx:
            raise InconsistencyError(message=f"{exx}.")

    @atomic()
    async def update(self, alter_user: EntityId, entity_id: EntityId, dto: access.SystemUser.UpdateDto) -> EntityId:
        await EntityRepository.check_not_exist_or_delete(SystemUser, entity_id)

        crypted_password = salt = None

        if dto.password:
            crypted_password, salt = BaseCrypto.encrypt_password(dto.password)

        system_user = await SystemUser.get_or_none(id=entity_id)
        try:
            system_user.first_name = dto.first_name or system_user.first_name
            system_user.last_name = dto.last_name or system_user.last_name
            system_user.middle_name = dto.middle_name or system_user.middle_name
            system_user.username = dto.username or system_user.username
            system_user.password = crypted_password or system_user.password
            system_user.salt = salt or system_user.salt
            system_user.phone = dto.phone or system_user.phone
            system_user.email = dto.email or system_user.email

            if dto.scopes:
                roles = await Role.filter(id__in=dto.scopes)
                for role in roles:
                    await system_user.scopes.add(role)

            await system_user.save()
            return entity_id

        except exceptions.ValidationError as ex:
            raise InconsistencyError(message=f"There is validation problem with {ex}.")
        except Exception:
            raise InconsistencyError(message=f"There is a problem updating user with id = {entity_id}.")

    @atomic()
    async def delete(self, alter_user: EntityId, entity_id: EntityId) -> EntityId:
        await EntityRepository.check_not_exist_or_delete(SystemUser, entity_id)
        await SystemUser.filter(id=entity_id).update(deleted=True)
        return entity_id


class ZoneAccess(BaseAccess):
    target_model = Zone

    @atomic()
    async def create(self, alter_user: EntityId, dto: access.Zone.CreationDto) -> AbstractBaseModel:
        return await super().create(alter_user, dto)

    @atomic()
    async def update(self, alter_user: EntityId, entity_id: EntityId, dto: access.Zone.UpdateDto) -> EntityId:
        zone = await Zone.get_or_none(id=entity_id)
        if zone is None:
            raise InconsistencyError(message=f"Such {alter_user} does not exist.")
        try:
            zone.name = dto.name
            await zone.save()
            return entity_id
        except Exception as exx:
            raise InconsistencyError(message=f"{exx}.")

    @atomic()
    async def delete(self, alter_user: EntityId, entity_id: EntityId) -> EntityId:
        zone = await Zone.get_or_none(id=entity_id)
        if zone is None:
            raise InconsistencyError(message=f"Zone with id={entity_id} does not exist.")
        await zone.delete()
        return entity_id


class ClaimWayAccess(BaseAccess):
    target_model = ClaimWay

    @staticmethod
    async def add_roles_and_users(claim_way: ClaimWay, dto: Union[access.ClaimWay.CreationDto,
                                                                  access.ClaimWay.UpdateDto]) -> None:
        """Add Roles and SystemUsers to ClaimWay"""
        if dto.system_users:
            sys_users = await SystemUser.filter(id__in=dto.system_users)
            for user in sys_users:
                await claim_way.system_users.add(user)

        if dto.roles:
            roles = await Role.filter(id__in=dto.roles)
            for role in roles:
                await claim_way.roles.add(role)

    @atomic()
    async def create(self, alter_user: EntityId, dto: access.ClaimWay.CreationDto) -> ClaimWay:
        try:
            claim_way = await ClaimWay.create()

            await self.add_roles_and_users(claim_way, dto)

            return claim_way

        except Exception as ex:
            raise InconsistencyError(message=f"{ex} while creating ClaimWay.")

    @atomic()
    async def update(self, alter_user: EntityId, entity_id: EntityId, dto: access.ClaimWay.UpdateDto) -> EntityId:
        try:
            claim_way = await ClaimWay.get_or_none(id=entity_id)
            if claim_way is None:
                raise InconsistencyError(message=f"ClaimWay with id={entity_id} does not exist.")

            await self.add_roles_and_users(claim_way, dto)

            return entity_id
        except Exception as ex:
            raise InconsistencyError(message=f"{ex} while updating ClaimWay.")

    @atomic()
    async def delete(self, alter_user: EntityId, entity_id: EntityId) -> EntityId:
        try:
            claim_way = await ClaimWay.get_or_none(id=entity_id)
            if claim_way is None:
                raise InconsistencyError(message=f"ClaimWay with id={entity_id} does not exist.")

            await claim_way.delete()
            return entity_id

        except Exception as ex:
            raise InconsistencyError(message=f"{ex} while deleting ClaimWay.")


class ClaimToZoneAccess(BaseAccess):
    target_model = ClaimToZone

    @atomic()
    async def create(self, alter_user: EntityId, dto: access.ClaimToZone.CreationDto) -> ClaimToZone:
        try:
            claim = await Claim.get_or_none(id=dto.claim)

            if claim is None:
                raise InconsistencyError(message=f"Claim {dto.claim} does not exist.")

            pass_id = None
            if dto.pass_id:
                pass_id = await Pass.get_or_none(id=dto.pass_id)

            claim_to_zone = await ClaimToZone.create(claim=claim,
                                                     pass_id=pass_id)

            zones = await Zone.filter(id__in=dto.zones)
            for zone in zones:
                await claim_to_zone.zones.add(zone)

            return claim_to_zone

        except Exception as ex:
            raise InconsistencyError(message=f"{ex}.")

    @atomic()
    async def update(self, alter_user: EntityId, entity_id: EntityId, dto: access.ClaimToZone.UpdateDto) -> EntityId:
        try:
            claimtozone_exist = await ClaimToZone.exists(id=entity_id)
            if claimtozone_exist is None:
                raise InconsistencyError(message=f"ClaimToZone with id={entity_id} does not exist.")

            claim_to_zone = await self.read(entity_id)

            pass_id = claim = None

            if dto.pass_id:
                pass_id = await Pass.get_or_none(id=dto.pass_id)

            if dto.claim:
                claim = await Claim.get_or_none(id=dto.claim)

            claim_to_zone.claim = claim or claim_to_zone.claim
            claim_to_zone.pass_id = pass_id or claim_to_zone.pass_id

            await claim_to_zone.save()

            if dto.zones:
                zones = await Zone.filter(id__in=dto.zones)
                for zone in zones:
                    await claim_to_zone.zones.add(zone)

            return entity_id

        except Exception as ex:
            raise InconsistencyError(message=f"{ex}")

    @atomic()
    async def delete(self, alter_user: EntityId, entity_id: EntityId) -> EntityId:
        claim_to_zone = await ClaimToZone.get_or_none(id=entity_id)
        if claim_to_zone is None:
            raise InconsistencyError(message=f"ClaimToZone with id={entity_id} does not exist.")
        await claim_to_zone.delete()
        return entity_id


class ParkingPlaceAccess(BaseAccess):
    target_model = ParkingPlace

    @atomic()
    async def create(self, alter_user: EntityId, dto: access.ParkingPlace.CreationDto) -> ParkingPlace:
        try:
            acquire_parking_intervals = await AcquireParkingInterval.get_or_none(id=dto.acquire_parking_intervals)
            if acquire_parking_intervals is None:
                raise InconsistencyError(message=f"Parking interval {dto.acquire_parking_intervals} does not exist.")

            parking_place = await ParkingPlace.create(real_number=dto.real_number,
                                                      acquire_parking_intervals=acquire_parking_intervals)
            return parking_place

        except Exception as ex:
            raise InconsistencyError(message=f"{ex}.")

    @atomic()
    async def update(self,
                     alter_user: EntityId,
                     entity_id: EntityId,
                     dto: access.ParkingPlace.UpdateDto) -> EntityId:
        try:
            parking_place = await self.read(entity_id)

            if parking_place is None:
                raise InconsistencyError(message=f"ParkingPlace with id={entity_id} does not exist.")

            acquire_parking_intervals = None
            if dto.acquire_parking_intervals:
                acquire_parking_intervals = await AcquireParkingInterval.get_or_none(id=dto.acquire_parking_intervals)

            if dto.enable is not None:
                parking_place.enable = False if dto.enable is False else True

            parking_place.acquire_parking_intervals = acquire_parking_intervals or \
                                                      parking_place.acquire_parking_intervals
            parking_place.real_number = dto.real_number or parking_place.real_number

            await parking_place.save()
            return entity_id
        except Exception as ex:
            raise InconsistencyError(message=f"{ex}")

    @atomic()
    async def delete(self, alter_user: EntityId, entity_id: EntityId) -> EntityId:
        parking_place = await ParkingPlace.get_or_none(id=entity_id)
        if parking_place is None:
            raise InconsistencyError(message=f"ParkingPlace with id={entity_id} does not exist.")

        await parking_place.delete()
        return entity_id


class ParkingAccess(BaseAccess):
    target_model = Parking

    @atomic()
    async def create(self, alter_user: EntityId, dto: access.Parking.CreationDto) -> Parking:

        parking_places = await ParkingPlace.get_or_none(id=dto.parking_places)

        current_places = None
        if dto.current_places:
            current_places = dto.current_places

        time_slot_interval = None
        if dto.time_slot_interval:
            time_slot_interval = dto.time_slot_interval

        parking = await Parking.create(max_places=dto.max_places,
                                       current_places=current_places,
                                       time_slot_interval=time_slot_interval,
                                       parking_places=parking_places)
        return parking

    @atomic()
    async def update(self, alter_user: EntityId, entity_id: EntityId, dto: access.Parking.UpdateDto) -> EntityId:
        parking = await self.read(entity_id)
        if parking is None:
            raise InconsistencyError(message=f"Parking with id={entity_id} does not exist")

        parking_places = await ParkingPlace.get_or_none(id=dto.parking_places)

        parking.max_places = dto.max_places or parking.max_places
        parking.current_places = dto.current_places or parking.current_places
        parking.time_slot_interval = dto.time_slot_interval or parking.time_slot_interval
        parking.parking_places = parking_places or parking.parking_places

        await parking.save()
        return entity_id

    @atomic()
    async def delete(self, alter_user: EntityId, entity_id: EntityId) -> EntityId:
        parking = await Parking.get_or_none(id=entity_id)
        if parking is None:
            raise InconsistencyError(message=f"Parking with id={entity_id} does not exist.")

        await parking.delete()
        return entity_id


class RoleAccess(BaseAccess):
    target_model = Role

    @atomic()
    async def create(self, alter_user: EntityId, dto: access.Role.CreationDto) -> AbstractBaseModel:
        return await super().create(alter_user, dto)

    @atomic()
    async def update(self, alter_user: EntityId, entity_id: EntityId, dto: access.Role.UpdateDto) -> EntityId:
        role = await Role.get_or_none(id=entity_id)
        if role is None:
            raise InconsistencyError(message=f"Role with id={entity_id} does not exist")

        role.name = dto.name
        await role.save()

        return entity_id

    @atomic()
    async def delete(self, alter_user: EntityId, entity_id: EntityId) -> EntityId:
        role = await Role.get_or_none(id=entity_id)
        if role is None:
            raise InconsistencyError(message=f"Role with id={entity_id} does not exist.")

        await role.delete()
        return entity_id
