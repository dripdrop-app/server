import asyncio
import threading
from typing import Union
from starlette.concurrency import run_in_threadpool


class AsyncioWorker():
    def __init__(self) -> None:
        self._tasks: list[Union[asyncio.Task, threading.Thread]] = []
        self._main_thread = threading.Thread(
            None, asyncio.run, args=[self.work()])

    def add_job(self, func, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            task = asyncio.create_task(func(*args, **kwargs))
        else:
            task = asyncio.create_task(
                run_in_threadpool(func, *args, **kwargs))

        self._tasks.append(task)

    def run(self):
        self._main_thread.start()

    def end(self):
        self._main_thread.join(30)

    async def work(self):
        try:
            while True:
                new_tasks = []
                for task in self._tasks:
                    if task.done():
                        new_tasks.append(task)
                self._tasks = new_tasks
                await asyncio.sleep(1)
        except Exception as e:
            for task in self._tasks:
                task.cancel()
            raise Exception(e)


Worker = AsyncioWorker()
