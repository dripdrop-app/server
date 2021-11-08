from enum import Enum


class RedisChannels(Enum):
    COMPLETED_JOB_CHANNEL = 'completed_jobs'
    STARTED_JOB_CHANNEL = 'started_jobs'


class AuthScopes(Enum):
    AUTHENTICATED = 'authenticated'
    ADMIN = 'admin'
    API_KEY = 'api_key'
