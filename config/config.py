import json
from pydantic import BaseModel


class ConfPD(BaseModel):
    some_conf: str


def get_config(json_conf_path: str) -> ConfPD:
    with open(json_conf_path, "r") as _json_file:
        return ConfPD(**json.loads(_json_file.read()))
