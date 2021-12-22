import aioredis
import anyio
import argparse
import asyncio
import functools
import importlib
import json
import os
import signal

# ADD JOB REQUEUING WHEN WORKER RESTARTS


class AsyncioQueue():
    def __init__(self, worker_channel: str, redis_url='redis://localhost:6379') -> None:
        self.worker_channel = worker_channel
        self.redis = aioredis.from_url(redis_url)

    async def enqueue(self, name: str, function_path: str, *args, **kwargs):
        job_running = await self.redis.get(name)
        if job_running:
            return
        await self.redis.set(name, 1)
        await self.redis.publish(self.worker_channel, json.dumps({
            'name': name,
            'module_path': '.'.join(function_path.split('.')[:-1]),
            'function_name': function_path.split('.')[-1],
            'args': args,
            'kwargs': kwargs
        }))


class AsyncioWorker():
    def __init__(self, worker_channel: str, redis_url: str, worker_file: str) -> None:
        self.tasks: list[asyncio.Task] = []
        self.worker_channel = worker_channel
        self.redis = aioredis.from_url(redis_url)
        self.listener = None
        self.worker_file = worker_file
        if worker_file:
            pid = str(os.getpid())
            with open(args.p, 'w') as f:
                f.write(pid + '\n')

    def add_job(self, name, module_path, function_name, *args, **kwargs):
        module = importlib.import_module(module_path)
        func = getattr(module, function_name)
        if asyncio.iscoroutinefunction(func):
            task = asyncio.create_task(func(*args, **kwargs), name=name)
        else:
            if kwargs:
                func = functools.partial(func, **kwargs)
            task = asyncio.create_task(
                anyio.to_thread.run_sync(func, *args, cancellable=True), name=name)
        self.tasks.append(task)

    async def _job_listener(self):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self.worker_channel)
        while True:
            try:
                message = await pubsub.get_message(True)
                if message is not None:
                    job_info = json.loads(message['data'].decode())
                    self.add_job(
                        job_info['name'],
                        job_info['module_path'],
                        job_info['function_name'],
                        *job_info['args'],
                        **job_info['kwargs']
                    )

                await asyncio.sleep(1)
            except Exception as e:
                print(e)
                pass

    def cleanup(self, sig, frame):
        print('CLEANING UP')
        self.listener.cancel()
        for task in self.tasks:
            task.cancel()
        if self.worker_file:
            os.remove(self.worker_file)

    async def work(self):
        try:
            self.listener = asyncio.create_task(self._job_listener())
            print('WORKER STARTED')
            while True:
                new_tasks = []
                for task in self.tasks:
                    if task.done():
                        await self.redis.delete(task.get_name())
                        exception = task.exception()
                        if exception:
                            print(exception)
                    else:
                        new_tasks.append(task)
                self.tasks = new_tasks
                if self.listener.done():
                    exception = self.listener.exception()
                    raise(exception)

                await asyncio.sleep(1)
        except Exception as e:
            print('ENDING WORKER')
            self.cleanup()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Asyncio worker')
    parser.add_argument('--channel')
    parser.add_argument('--redis-url', default='redis://localhost:6379')
    parser.add_argument('-p')

    args = parser.parse_args()
    worker = AsyncioWorker(worker_channel=args.channel,
                           redis_url=args.redis_url, worker_file=args.p)
    signal.signal(signal.SIGINT, worker.cleanup)
    asyncio.run(worker.work())
