from pydantic import BaseModel, ConfigDict
import uuid

class UserBase(BaseModel):
    name: str | None = None
    #Change it later to EmailSTR
    email: str

class UserCreate(UserBase):
    password: str
    is_active: bool | None = False
    auth_provider: str = 'local'


class UserUpdate(BaseModel):
    email: str | None = None
    number: str | None = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    number: str | None

    model_config = ConfigDict(from_attributes=True)
    