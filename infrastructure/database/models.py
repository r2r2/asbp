import re
from datetime import datetime
from tortoise import fields
from tortoise.models import Model
from tortoise.validators import RegexValidator

import settings


class AbstractBaseModel(Model):
    """Базовая модель"""
    id = fields.IntField(pk=True)

    async def values_dict(self, m2m_fields: bool = False, fk_fields: bool = False, drop_cols: list[str] = None) -> dict:
        t_d = {}
        for k, v in self.__dict__.items():
            if k == "alteration_info_id":
                continue
            if isinstance(v, datetime):
                v = v.astimezone().strftime("%d.%m.%Y, %H:%M:%S %z")
            if not k.startswith('_'):
                t_d.update({k: v})
        if fk_fields:
            for field in self._meta.fk_fields:
                model = await getattr(self, field)
                if model and not isinstance(model, AlterationInfo):
                    t_d.update({field: await model.values_dict()})
        if m2m_fields:
            for field in self._meta.m2m_fields:
                t_d.update({field: [await i.values_dict() for i in await getattr(self, field) if i]})
        if drop_cols:
            for drops in drop_cols:
                if drops in t_d:
                    t_d.pop(drops)
        return t_d

    class Meta:
        abstract = True


class TimestampMixin:
    """Общий миксин даты создания и изменения"""
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)


class FakeDeleted:
    """Помечает объект удаленным, вместо удаления"""
    deleted = fields.BooleanField(default=False)


# ------------------------------------USER---------------------------------

class SystemUser(AbstractBaseModel, TimestampMixin, FakeDeleted):
    """Сотрудник компании"""
    first_name = fields.CharField(max_length=24, description="Имя")
    last_name = fields.CharField(max_length=24, description="Фамилия")
    middle_name = fields.CharField(max_length=24, null=True, description="Отчество")
    username = fields.CharField(max_length=24, unique=True)
    password = fields.TextField()
    salt = fields.TextField()
    last_login = fields.DatetimeField(default=None, null=True)
    last_logout = fields.DatetimeField(default=None, null=True)
    expire_session_delta = fields.IntField(default=86400)
    phone = fields.CharField(max_length=24, null=True, validators=[RegexValidator(settings.PHONE_NUMBER, re.I)])
    email = fields.CharField(max_length=36, null=True)
    scopes: fields.ManyToManyRelation["Role"] = fields.ManyToManyField(
        'asbp.Role', related_name='scopes', through='role_systemuser'
    )

    claim_ways: fields.ManyToManyRelation["ClaimWay"]
    system_user_session: fields.ReverseRelation["SystemUserSession"]
    active_dir: fields.ReverseRelation["ActiveDir"]

    def __repr__(self) -> str:
        return f"{self.username}: {self.first_name} {self.last_name}"

    def to_dict(self) -> dict:
        return {"user_id": self.id, "username": self.username,
                "scopes": [i.name for i in self.scopes]}


class SystemUserSession(AbstractBaseModel):
    """Данные сессии сотрудника компании"""
    user: fields.ForeignKeyNullableRelation["SystemUser"] = fields.ForeignKeyField(
        "asbp.SystemUser", null=True, on_delete=fields.CASCADE
    )
    expire_time = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True, null=True)
    logout_time = fields.DatetimeField(null=True)
    user_agent = fields.TextField(null=True)
    salt = fields.TextField()
    nonce = fields.TextField()
    tag = fields.TextField()


class Role(AbstractBaseModel, TimestampMixin):
    """Роли пользователей для согласований"""
    name = fields.CharField(max_length=24, description='Название роли')

    system_user: fields.ManyToManyRelation["SystemUser"]
    claim_ways: fields.ManyToManyRelation["ClaimWay"]

    def __repr__(self) -> str:
        return f"{self.name}"


class ActiveDir(AbstractBaseModel):
    """Данные пользователя из Active Directory"""
    user: fields.ForeignKeyRelation["SystemUser"] = fields.ForeignKeyField(
        "asbp.SystemUser", on_delete=fields.CASCADE, related_name='user'
    )
    sid = fields.CharField(max_length=128, null=True, description='SID пользователя')


# ------------------------------------VISITOR---------------------------------


class Visitor(AbstractBaseModel, TimestampMixin, FakeDeleted):
    """Посетитель"""
    first_name = fields.CharField(max_length=24, description="Имя")
    last_name = fields.CharField(max_length=24, description="Фамилия")
    middle_name = fields.CharField(max_length=24, null=True, description="Отчество")
    who_invited = fields.CharField(max_length=64, null=True, description='Кто пригласил?')
    destination = fields.CharField(max_length=128, null=True, description='Куда идет?')
    # TODO decide about on_delete
    passport: fields.OneToOneNullableRelation["Passport"] = fields.OneToOneField(
        'asbp.Passport', on_delete=fields.CASCADE, related_name='passport', null=True
    )
    pass_id: fields.OneToOneNullableRelation["Pass"] = fields.OneToOneField(
        'asbp.Pass', on_delete=fields.CASCADE, related_name='pass_visitor', null=True
    )
    drive_license: fields.OneToOneNullableRelation["DriveLicense"] = fields.OneToOneField(
        'asbp.DriveLicense', on_delete=fields.CASCADE, related_name='drive_license', null=True
    )
    visitor_foto: fields.OneToOneNullableRelation["VisitorFoto"] = fields.OneToOneField(  # TODO !photo!
        'asbp.VisitorFoto', on_delete=fields.CASCADE, related_name='visitor_foto', null=True
    )
    transport: fields.ForeignKeyNullableRelation["Transport"] = fields.ForeignKeyField(
        'asbp.Transport', on_delete=fields.CASCADE, related_name='transport', null=True
    )
    military_id: fields.OneToOneNullableRelation["MilitaryId"] = fields.OneToOneField(
        'asbp.MilitaryId', on_delete=fields.CASCADE, related_name='military_id', null=True
    )
    claim: fields.ForeignKeyNullableRelation["Claim"] = fields.ForeignKeyField(
        'asbp.Claim', on_delete=fields.CASCADE, related_name='visitor_claim', null=True
    )

    black_lists: fields.ReverseRelation["BlackList"]
    visit_sessions: fields.ReverseRelation["VisitSession"]

    def __repr__(self) -> str:
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class VisitSession(AbstractBaseModel, TimestampMixin):
    """Время посещения"""
    visitor: fields.ForeignKeyRelation["Visitor"] = fields.ForeignKeyField(
        'asbp.Visitor', on_delete=fields.CASCADE, related_name='visitors'
    )
    enter = fields.DatetimeField(description='Зашел на территорию', null=True)
    exit = fields.DatetimeField(description='Вышел с территории', null=True)


class Passport(AbstractBaseModel, TimestampMixin):
    """Данные паспорта"""
    number = fields.BigIntField(description='Номер паспорта', unique=True)
    division_code = fields.CharField(max_length=7, description='Код подразделения', null=True)
    registration = fields.CharField(max_length=255, description='Прописка', null=True)
    date_of_birth = fields.DatetimeField(description='Дата рождения', null=True)
    place_of_birth = fields.CharField(max_length=255, description='Место рождения', null=True)
    gender = fields.CharField(max_length=8, description='Пол', null=True)

    visitor: fields.ReverseRelation["Visitor"]

    def __repr__(self) -> str:
        return f"Номер паспорта: {self.number}"


class DriveLicense(AbstractBaseModel, TimestampMixin):
    """Водительское удостоверение"""
    date_of_issue = fields.DatetimeField(null=True, description='Дата выдачи водительского удостоверения')
    expiration_date = fields.DatetimeField(null=True, description='Дата окончания действия водительского удостоверения')
    place_of_issue = fields.CharField(max_length=64, null=True, description='Орган выдавший водительское удостоверение')
    address_of_issue = fields.CharField(
        max_length=64, null=True, description='Регион, где было выдано водительское удостоверение'
    )
    number = fields.BigIntField(unique=True, max_length=24, description='Номер водительского удостоверения')
    categories = fields.CharField(max_length=16, null=True, description='Открытые категории')

    visitor: fields.ReverseRelation["Visitor"]

    def __repr__(self) -> str:
        return f"Номер водительского удостоверения: {self.number}"


class VisitorFoto(AbstractBaseModel, TimestampMixin):
    """Фото посетителя"""
    signature = fields.JSONField(null=True)
    webcam_img = fields.BinaryField(null=True, description='Фото с веб-камеры')
    scan_img = fields.BinaryField(null=True, description='Скан документа')
    car_number_img = fields.BinaryField(null=True, description='Фото номера транспорта')

    visitor: fields.ReverseRelation["Visitor"]


class MilitaryId(AbstractBaseModel, TimestampMixin):
    """Военный билет"""
    number = fields.CharField(max_length=16, description='Номер военного билета')
    date_of_birth = fields.DatetimeField(description='Дата рождения', null=True)
    place_of_issue = fields.CharField(max_length=64, null=True, description='Орган выдавший военный билет')
    date_of_issue = fields.DatetimeField(null=True, description='Дата выдачи военного билета')
    place_of_birth = fields.CharField(max_length=255, description='Место рождения', null=True)

    visitor: fields.ReverseRelation["Visitor"]

    def __repr__(self) -> str:
        return f"{self.number}"


# ------------------------------------CLAIM---------------------------------

class Claim(AbstractBaseModel, TimestampMixin):
    """Заявка на пропуск"""
    claim_way: fields.ForeignKeyNullableRelation["ClaimWay"] = fields.ForeignKeyField(
        'asbp.ClaimWay', on_delete=fields.CASCADE, related_name='claim_way', null=True
    )
    pass_id: fields.ForeignKeyNullableRelation["Pass"] = fields.ForeignKeyField(
        'asbp.Pass', on_delete=fields.CASCADE, related_name='pass_claim', null=True
    )
    pass_type = fields.CharField(max_length=24, description='Тип пропуска (разовый/временный/материальный)')
    approved = fields.BooleanField(default=False, description='Заявка одобрена?')
    is_in_blacklist = fields.BooleanField(default=False, description='В черном списке?')
    pnd_agreement = fields.BooleanField(default=False, description='Согласие на обработку ПНД')
    information = fields.CharField(max_length=255, null=True, description='Любая информация о заявке')
    status = fields.CharField(max_length=128, description='Статус заявки(действующая/отработана/просрочена)')

    claim_to_zone: fields.ReverseRelation["ClaimToZone"]
    transports: fields.ManyToManyRelation["Transport"]
    visitor_claim: fields.ReverseRelation["Visitor"]


class Pass(AbstractBaseModel, TimestampMixin):
    """Пропуск"""
    rfid = fields.BigIntField(null=True)
    pass_type = fields.CharField(max_length=16, description='Тип пропуска (бумажный/карта/лицо)')
    valid_till = fields.DatetimeField(description='До какого числа действует пропуск')
    valid = fields.BooleanField(default=True, description='Пропуск действителен?')

    visitor: fields.ReverseRelation["Visitor"]
    claim: fields.ReverseRelation["Claim"]
    claim_to_zones: fields.ReverseRelation["ClaimToZone"]

    def __repr__(self) -> str:
        return f"Pass type: {self.pass_type}"


class ClaimWay(AbstractBaseModel, TimestampMixin):
    """Маршрут согласования заявки"""
    system_users: fields.ManyToManyRelation["SystemUser"] = fields.ManyToManyField(
        'asbp.SystemUser', related_name='claim_ways', through='claimway_systemuser'
    )
    roles: fields.ManyToManyRelation["Role"] = fields.ManyToManyField(
        'asbp.Role', related_name='roles', through='claimway_role'
    )

    claims: fields.ReverseRelation["Claim"]


class Zone(AbstractBaseModel, TimestampMixin):
    """Зоны доступа, разрешенные для посещения"""
    name = fields.CharField(max_length=128, description='Название территории')

    claim_to_zones: fields.ManyToManyRelation["ClaimToZone"]

    def __repr__(self) -> str:
        return f"{self.name}"


class ClaimToZone(AbstractBaseModel, TimestampMixin):
    """Заявка на посещение конкретной зоны"""
    claim: fields.ForeignKeyRelation["Claim"] = fields.ForeignKeyField(
        'asbp.Claim', on_delete=fields.CASCADE, related_name='claims'
    )
    zones: fields.ManyToManyRelation["Zone"] = fields.ManyToManyField(
        'asbp.Zone', related_name='claim_to_zones', through='claimtozone_zone'
    )
    pass_id: fields.ForeignKeyNullableRelation["Pass"] = fields.ForeignKeyField(
        'asbp.Pass', on_delete=fields.CASCADE, related_name='pass', null=True
    )


# ------------------------------------TRANSPORT---------------------------------


class Transport(AbstractBaseModel, TimestampMixin):
    """Данные транспорта"""
    model = fields.CharField(max_length=16, null=True)
    number = fields.CharField(max_length=16, description='Регистрационный номер', unique=True)
    color = fields.CharField(max_length=16, description='Цвет', null=True)
    claims: fields.ManyToManyRelation["Claim"] = fields.ManyToManyField(
        'asbp.Claim', related_name='transports', through='transport_claim'
    )
    parking_places: fields.ForeignKeyNullableRelation["ParkingPlace"] = fields.ForeignKeyField(
        'asbp.ParkingPlace', on_delete=fields.CASCADE, related_name='parking_places', null=True
    )

    visitors: fields.ReverseRelation["Visitor"]

    def __repr__(self) -> str:
        return f"{self.number}"


class ParkingPlace(AbstractBaseModel, TimestampMixin):
    """Парковочное место"""
    enable = fields.BooleanField(default=True)
    real_number = fields.SmallIntField(description='Номер парковочного места')
    acquire_parking_intervals: fields.ForeignKeyNullableRelation["AcquireParkingInterval"] = fields.ForeignKeyField(
        'asbp.AcquireParkingInterval', on_delete=fields.CASCADE, related_name='parking_places', null=True
    )

    parking: fields.ReverseRelation["Parking"]
    transports: fields.ReverseRelation["Transport"]


class Parking(AbstractBaseModel, TimestampMixin):
    """Вся парковка"""
    max_places = fields.SmallIntField(description='Общее количество парковочных мест')
    current_places = fields.SmallIntField(null=True, description='Текущее количество мест')
    time_slot_interval = fields.IntField(null=True)

    parking_places: fields.ForeignKeyNullableRelation["ParkingPlace"] = fields.ForeignKeyField(
        'asbp.ParkingPlace', on_delete=fields.CASCADE, related_name='parking', null=True
    )


class AcquireParkingInterval(AbstractBaseModel, TimestampMixin):
    """Получить временной интервал для парковки авто"""
    start_interval = fields.DatetimeField()
    end_interval = fields.DatetimeField()
    # transport: fields.OneToOneRelation["Transport"] = fields.OneToOneField(
    #     'asbp.Transport', on_delete=fields.CASCADE, related_name='acquire_parking_interval'
    # )
    reserved_interval: fields.ForeignKeyRelation["ParkingTimeSlot"] = fields.ForeignKeyField(
        'asbp.ParkingTimeSlot', related_name='reserved_interval', on_delete=fields.CASCADE
    )

    parking_places: fields.ReverseRelation["ParkingPlace"]


class ParkingTimeSlot(AbstractBaseModel, TimestampMixin):
    """Парковочные временные слоты"""
    start = fields.DatetimeField()
    end = fields.DatetimeField()
    enable = fields.BooleanField(default=True)

    acquire_parking_intervals: fields.ReverseRelation["AcquireParkingInterval"]


# ------------------------------------SYSTEM---------------------------------

class BlackList(AbstractBaseModel, TimestampMixin):
    """Черный список"""
    visitor: fields.ForeignKeyRelation["Visitor"] = fields.ForeignKeyField(
        'asbp.Visitor', on_delete=fields.CASCADE, related_name='visitor'
    )
    level = fields.CharField(max_length=24, description='Уровни нарушений', null=True)


class Plugin(AbstractBaseModel):
    filename = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255)
    enabled = fields.BooleanField(default=False)


class AlterationInfo:
    pass
