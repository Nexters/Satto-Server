from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config.config import db_config
from src.config.database import Mysql


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.mysql = Mysql(db_config)

        yield

    finally:

        await app.state.mysql.close()
