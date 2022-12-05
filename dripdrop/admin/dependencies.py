from fastapi import Depends, status, HTTPException
from dripdrop.authentication.models import User
from dripdrop.dependencies import get_user
from typing import Union


async def get_admin_user(user: Union[None, User] = Depends(get_user)):
    if user and user.admin:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
