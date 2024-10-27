import uuid

from pydantic import BaseModel, field_validator, Field

from src.core.secure import decrypt_token


class UserInput(BaseModel):
    name: str = Field(description="Foo name", default="Bar name")
    token: str = Field(description="FooBarToken")

class UserOutput(UserInput):
    id: uuid.UUID

    @field_validator("token")
    def validate_login(cls, token: str):
        return decrypt_token(token)







