from pydantic import BaseModel


class ClientModel(BaseModel):
    id: int
    name: str
    phone: str


class CreateClientModel(BaseModel):
    name: str
    phone: str
