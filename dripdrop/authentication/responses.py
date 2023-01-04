from fastapi import status
from fastapi.responses import JSONResponse

from dripdrop.dependencies import COOKIE_NAME
from dripdrop.responses import ResponseBaseModel
from dripdrop.settings import settings

from .models import User

TWO_WEEKS_EXPIRATION = 14 * 24 * 60 * 60


class UserResponseModel(ResponseBaseModel):
    email: str
    admin: bool


class UserResponse(JSONResponse):
    def __init__(self, user: User = ...):
        super().__init__(
            content=UserResponseModel(email=user.email, admin=user.admin).dict(
                by_alias=True
            ),
            status_code=status.HTTP_200_OK,
        )


class AuthenticatedResponseModel(ResponseBaseModel):
    access_token: str
    token_type: str
    user: UserResponseModel


class AuthenticatedResponse(JSONResponse):
    def __init__(self, access_token: str = ..., user: UserResponseModel = ...):
        super().__init__(
            content=AuthenticatedResponseModel(
                access_token=access_token, user=user, token_type="Bearer"
            ).dict(by_alias=True),
            status_code=status.HTTP_200_OK,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.set_cookie(
            COOKIE_NAME,
            value=access_token,
            expires=TWO_WEEKS_EXPIRATION,
            max_age=TWO_WEEKS_EXPIRATION,
            httponly=True,
            secure=settings.env == "production",
        )


class ErrorMessages:
    IncorrectCredentials = "Incorrect Credentials"
    AccountExists = "Account Exists"
