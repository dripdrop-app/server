from fastapi import Depends, status, HTTPException

from dripdrop.apps.authentication.models import User
from dripdrop.dependencies import get_authenticated_user


async def get_admin_user(user: User = Depends(get_authenticated_user)):
    if user.admin:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
