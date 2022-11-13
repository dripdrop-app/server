from dripdrop.models import User
from pydantic import BaseModel, SecretStr, Field


class UserResponse(User):
    password: SecretStr = Field(..., exclude=True)


class AuthenticatedResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class IncorrectCredentialsResponse(BaseModel):
    error = "Incorrect Credentials"
