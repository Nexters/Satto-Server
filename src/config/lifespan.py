from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.common.logger import start_logging
from src.config.config import db_config
from src.config.database import Mysql


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.log_processor_task = await start_logging()
        app.state.mysql = Mysql(db_config)
        yield

    finally:
        if hasattr(app.state, "log_processor_task"):
            app.state.log_processor_task.cancel()
            try:
                await app.state.log_processor_task
            except Exception:
                pass  # Ignore exceptions during task cancellation
        await app.state.mysql.close()

