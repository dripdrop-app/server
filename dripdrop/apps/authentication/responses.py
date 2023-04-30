from fastapi import status
from fastapi.responses import JSONResponse

from dripdrop.apps.authentication.dependencies import COOKIE_NAME
from dripdrop.responses import ResponseBaseModel
from dripdrop.settings import settings, ENV


TWO_WEEKS_EXPIRATION = 14 * 24 * 60 * 60


class UserResponse(ResponseBaseModel):
    email: str
    admin: bool


class AuthenticatedResponseModel(ResponseBaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class AuthenticatedResponse(JSONResponse):
    def __init__(self, access_token: str, user: UserResponse):
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
            secure=settings.env == ENV.PRODUCTION,
        )


class ErrorMessages:
    IncorrectCredentials = "Incorrect Credentials"
    AccountExists = "Account Exists"
