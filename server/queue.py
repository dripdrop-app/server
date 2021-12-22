from worker import AsyncioQueue
from server.utils.enums import RedisChannels

queue = AsyncioQueue(RedisChannels.WORK_CHANNEL.value)
