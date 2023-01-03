from fastapi import Depends, status, HTTPException
from typing import Union

from dripdrop.authentication.models import User
from dripdrop.dependencies import get_user


async def get_admin_user(user: Union[None, User] = Depends(get_user)):
    if user and user.admin:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
