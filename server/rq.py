from croniter import croniter
from datetime import datetime, timedelta, timezone
from redis import Redis
from rq import Queue
from rq.registry import ScheduledJobRegistry

queue = Queue(connection=Redis(), default_timeout=-1)
scheduled_registry = ScheduledJobRegistry(queue=queue)

for job_id in scheduled_registry.get_job_ids():
    scheduled_registry.remove(job_id, delete_job=True)


def cron_job(cron_string: str, function: str, args=(), kwargs={}):
    est = timezone(timedelta(hours=-5))
    cron = croniter(cron_string, datetime.now(est))
    cron.get_next()
    next_run_time = cron.get_current(ret_type=datetime)
    print(f"Scheduling {function} to run at {next_run_time}")
    job = queue.enqueue_at(
        next_run_time,
        function,
        args=args,
        kwargs=kwargs,
    )
    queue.enqueue_call(
        "server.rq.cron_job",
        args=(cron_string, function),
        kwargs={"args": args, "kwargs": kwargs},
        depends_on=job,
    )
