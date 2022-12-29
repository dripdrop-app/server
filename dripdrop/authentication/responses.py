from datetime import datetime
from dripdrop.responses import ResponseBaseModel
from pydantic import SecretStr, Field


class UserResponse(ResponseBaseModel):
    email: str
    password: SecretStr = Field(..., exclude=True)
    admin: bool
    created_at: datetime = Field(..., exclude=True)


class AuthenticatedResponse(ResponseBaseModel):
    access_token: str
    token_type: str
    user: UserResponse


IncorrectCredentialsResponse = "Incorrect Credentials"

AccountExistsResponse = "Account Exists"
