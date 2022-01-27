from enum import Enum


class AuthScopes(Enum):
    AUTHENTICATED = "authenticated"
    ADMIN = "admin"
    API_KEY = "api_key"


class RequestMethods(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    HEAD = "HEAD"
