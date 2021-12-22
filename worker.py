import asyncio
import json
import importlib
from starlette.concurrency import run_in_threadpool
from server.redis import redis
from server.utils.enums import RedisChannels


class AsyncioQueue():
    async def enqueue(self, function_path: str, *args, **kwargs):
        await redis.publish(RedisChannels.WORK_CHANNEL.value, json.dumps({
            'module_path': '.'.join(function_path.split('.')[:-1]),
            'function_name': function_path.split('.')[-1],
            'args': args,
            'kwargs': kwargs
        }))


class AsyncioWorker():
    def __init__(self) -> None:
        self._tasks: list[asyncio.Task] = []

    def add_job(self, module_path, function_name, *args, **kwargs):
        module = importlib.import_module(module_path)
        func = getattr(module, function_name)
        if asyncio.iscoroutinefunction(func):
            task = asyncio.create_task(func(*args, **kwargs))
        else:
            task = asyncio.create_task(
                run_in_threadpool(func, *args, **kwargs))
        self._tasks.append(task)

    async def _job_listener(self):
        pubsub = redis.pubsub()
        await pubsub.subscribe(RedisChannels.WORK_CHANNEL.value)
        while True:
            try:
                message = await pubsub.get_message(True)
                if message is not None:
                    job_info = json.loads(message['data'].decode())
                    self.add_job(
                        job_info['module_path'],
                        job_info['function_name'],
                        *job_info['args'],
                        **job_info['kwargs']
                    )

                await asyncio.sleep(1)
            except Exception as e:
                print(e)
                pass

    async def work(self):
        try:
            listener = asyncio.create_task(self._job_listener())
            while True:
                new_tasks = []
                for task in self._tasks:
                    if task.done():
                        exception = task.exception()
                        if exception:
                            print(exception)
                    else:
                        new_tasks.append(task)
                self._tasks = new_tasks
                if listener.done():
                    exception = listener.exception()
                    raise(exception)

                await asyncio.sleep(1)
        except Exception as e:
            listener.cancel()
            for task in self._tasks:
                task.cancel()
            raise Exception(e)


Worker = AsyncioWorker()

if __name__ == '__main__':
    worker = AsyncioWorker()
    asyncio.run(worker.work())
