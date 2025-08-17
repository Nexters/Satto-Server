from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.common.scheduler.tasks import update_next_lotto_draw

scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

scheduler.add_job(update_next_lotto_draw, "cron", hour="21", minute="00")
