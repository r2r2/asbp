from core.dto.service import EmailStruct


class Event:
    name: str
    _description: str

    def __init__(self):
        if not self._description:
            self._description = ""

    async def to_dict(self) -> dict:
        raise NotImplementedError()

    async def to_redis(self) -> dict:
        pd = await self.to_dict()
        pd.update({"description": self._description})
        return pd

    async def to_celery(self) -> dict:
        raise NotImplementedError()

    @staticmethod
    def all_types():
        return [cls.name for cls in Event.__subclasses__()]


class NotifyVisitorInBlackListEvent(Event):
    name = "visitor_in_black_list"
    _security_users: EmailStruct

    def __init__(self, email_struct: EmailStruct):
        self._security_users = email_struct
        self._description = "Notifying security officers about visitor in black list."
        super().__init__()

    async def to_celery(self) -> dict:
        return await self.to_dict()

    async def to_dict(self) -> dict:
        return self._security_users.dict()


class NotifyUsersInClaimWayEvent(Event):
    name = "users_in_claimway"
    _system_users: EmailStruct

    def __init__(self, email_struct: EmailStruct):
        self._system_users = email_struct
        self._description = "Notifying system users marked in claim way."
        super().__init__()

    async def to_celery(self) -> dict:
        return await self.to_dict()

    async def to_dict(self) -> dict:
        return self._system_users.dict()
