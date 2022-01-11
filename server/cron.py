import asyncio
import time
from croniter import croniter
from datetime import datetime, timedelta, timezone
from threading import Thread


class Cron:
    def __init__(self) -> None:
        self.crons = []
        self.cron_threads: list[Thread] = []
        self.terminate = False

    def stop_thread(self):
        return self.terminate

    def add_cron(self, cron: str, func, args=(), kwargs={}):
        if not croniter.is_valid(cron):
            raise ValueError(f'Not a valid cron "{cron}"')
        self.crons.append({
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'cron': cron
        })

    def run(self):
        for cron in self.crons:
            func = cron.get('func')
            args = cron.get('args')
            kwargs = cron.get('kwargs')
            cron_time = cron.get('cron')
            thread = Thread(None, target=self.run_cron,
                            args=(func, args, kwargs, cron_time, self.stop_thread))
            thread.start()
            self.cron_threads.append(thread)

    def end(self):
        self.terminate = True
        for thread in self.cron_threads:
            thread.join(1)

    def run_cron(self, func, args, kwargs, cron_string, stop):
        est = timezone(timedelta(hours=-5))
        cron = croniter(cron_string, datetime.now(est))
        cron.get_next()
        while not stop():
            current_time = datetime.now(est).replace(microsecond=0)
            if cron.get_current() == current_time.timestamp():
                if asyncio.iscoroutinefunction(func):
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(func(*args, **kwargs))
                else:
                    func(*args, **kwargs)
                cron.get_next()
            time.sleep(1)
