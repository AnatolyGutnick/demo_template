"""Response contracts. `Model.model_validate(response.json())` fails loudly on a contract break."""

from pydantic import BaseModel, ConfigDict


class ExampleUser(BaseModel):
    model_config = ConfigDict(extra="forbid")  # unexpected fields = contract change worth flagging

    id: str
    name: str
    email: str
