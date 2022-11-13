from datetime import datetime
from dripdrop.models import User
from dripdrop.responses import ResponseBaseModel
from pydantic import SecretStr, Field


class UserResponse(User):
    password: SecretStr = Field(..., exclude=True)
    created_at: datetime = Field(..., exclude=True)


class AuthenticatedResponse(ResponseBaseModel):
    access_token: str
    token_type: str
    user: UserResponse


IncorrectCredentialsResponse = "Incorrect Credentials"

AccountExistsResponse = "Account Exists"
