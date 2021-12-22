import aioredis
import anyio
import argparse
import asyncio
import functools
import importlib
import json
import os


# ADD JOB REQUEUING WHEN WORKER RESTARTS

class AsyncioQueue():
    def __init__(self, worker_channel: str, redis_url='redis://localhost:6379') -> None:
        self.worker_channel = worker_channel
        self.redis = aioredis.from_url(redis_url)

    async def enqueue(self, function_path: str, *args, **kwargs):
        await self.redis.publish(self.worker_channel, json.dumps({
            'module_path': '.'.join(function_path.split('.')[:-1]),
            'function_name': function_path.split('.')[-1],
            'args': args,
            'kwargs': kwargs
        }))


class AsyncioWorker():
    def __init__(self, worker_channel: str, redis_url: str) -> None:
        self._tasks: list[asyncio.Task] = []
        self.worker_channel = worker_channel
        self.redis = aioredis.from_url(redis_url)

    def add_job(self, module_path, function_name, *args, **kwargs):
        module = importlib.import_module(module_path)
        func = getattr(module, function_name)
        if asyncio.iscoroutinefunction(func):
            task = asyncio.create_task(func(*args, **kwargs))
        else:
            if kwargs:
                func = functools.partial(func, **kwargs)
            task = asyncio.create_task(
                anyio.to_thread.run_sync(func, *args, cancellable=True))
        self._tasks.append(task)

    async def _job_listener(self):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self.worker_channel)
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Asyncio worker')
    parser.add_argument('--channel')
    parser.add_argument('--redis-url', default='redis://localhost:6379')
    parser.add_argument('-p')

    args = parser.parse_args()
    try:
        if args.p:
            pid = str(os.getpid())
            with open(args.p, 'w') as f:
                f.write(pid + '\n')

        worker = AsyncioWorker(worker_channel=args.channel,
                               redis_url=args.redis_url)
        asyncio.run(worker.work())
    except Exception as e:
        os.remove(args.p)
