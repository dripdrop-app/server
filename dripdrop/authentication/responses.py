from fastapi import status
from fastapi.responses import JSONResponse

from dripdrop.dependencies import COOKIE_NAME
from dripdrop.responses import ResponseBaseModel
from dripdrop.settings import settings

TWO_WEEKS_EXPIRATION = 14 * 24 * 60 * 60


class UserResponseModel(ResponseBaseModel):
    email: str
    admin: bool


class UserResponse(JSONResponse):
    def __init__(self, user: UserResponseModel = ...):
        super().__init__(content=user.dict(), status_code=status.HTTP_200_OK)


class AuthenticatedResponseModel(ResponseBaseModel):
    access_token: str
    token_type: str
    user: UserResponseModel


class AuthenticatedResponse(JSONResponse):
    def __init__(
        self, email: str = ..., access_token: str = ..., user: UserResponseModel = ...
    ):
        super().__init__(
            content=AuthenticatedResponseModel(
                email=email, access_token=access_token, user=user
            ).dict(),
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
