import secrets
import string
import urllib.parse
from datetime import timedelta
from typing import Any

import jwt
from fastapi import Request

from dripdrop.settings import ENV, settings
from dripdrop.utils import get_current_time

ALGORITHM = "HS256"


def create_jwt(email: str):
    return jwt.encode(
        payload={
            "email": email,
            "exp": get_current_time() + timedelta(days=14),
        },
        key=settings.secret_key,
        algorithm=ALGORITHM,
    )


def create_jwt_token(email: str, code: str):
    return jwt.encode(
        payload={
            "email": email,
            "code": code,
            "exp": get_current_time() + timedelta(seconds=3600),
        },
        key=settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, key=settings.secret_key, algorithms=[ALGORITHM])
        expires = payload.get("exp", None)
        if expires is None:
            return None
        if expires < get_current_time().timestamp():
            return None
        return payload
    except jwt.PyJWTError:
        return None


def generate_server_link(request: Request, path: str, query: dict[str, Any]):
    return urllib.parse.urlunsplit(
        (
            "https" if settings.env == ENV.PRODUCTION else "http",
            request.headers.get("Host", request.base_url),
            path,
            urllib.parse.urlencode(query),
            "",
        )
    )


def generate_random_string(length: int):
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
