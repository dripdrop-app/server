import asyncio
from datetime import datetime, timedelta, timezone
from server.queue import q


async def run_cron():
    while True:
        current_time = datetime.now(timezone(timedelta(hours=-5)))
        if current_time.minute % 5 == 0:
            print('CRON RUNNING ', current_time)
        if current_time.minute == 0 and current_time.hour == 1:
            q.enqueue('server.api.youtube.tasks.channel_cleanup')
        if current_time.minute == 0 and current_time.hour == 3:
            q.enqueue('server.api.youtube.tasks.update_youtube_video_categories')
        if current_time.minute == 0 and current_time.hour == 5:
            q.enqueue('server.api.youtube.tasks.update_channels')
        if current_time.minute == 0 and current_time.hour == 5 and current_time.weekday == 6:
            q.enqueue('server.api.youtube.tasks.update_subscriptions')
        await asyncio.sleep(60)

if __name__ == '__main__':
    asyncio.run(run_cron())
