"""Akeyless response contracts (only the fields the tests rely on).

`extra="ignore"`: the real responses carry many more fields; the contract pins what we use.
"""

from pydantic import BaseModel, ConfigDict


class _Contract(BaseModel):
    model_config = ConfigDict(extra="ignore")


class AuthOutput(_Contract):
    token: str
    expiration: str | None = None


class CreateAuthMethodOutput(_Contract):
    access_id: str
    access_key: str


class ApiError(_Contract):
    error: str
