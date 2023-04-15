import asyncio
from argparse import ArgumentParser

from dripdrop.logger import logger
from dripdrop.services.cron import start_cron_jobs, clear_cron_jobs


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--schedule", action="store_true", default=False)
    parser.add_argument("--clear-schedule", action="store_true", default=False)

    args = parser.parse_args()

    if args.schedule and args.clear_schedule:
        raise ValueError("Both schedule and clear schedule cannot be used")
    elif args.schedule:
        logger.info("Scheduling jobs...")
        asyncio.run(start_cron_jobs())
        logger.info("Finished scheduling jobs!")
    elif args.clear_schedule:
        logger.info("Clearing scheduled jobs...")
        asyncio.run(clear_cron_jobs())
        logger.info("Finished clearing jobs!")
