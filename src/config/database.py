from contextlib import asynccontextmanager
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.common.logger import logger
from src.config.config import db_config


class Base(DeclarativeBase):
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


class Mysql:
    def __init__(self, config: db_config) -> None:
        self.config = config

        self.engine = create_async_engine(
            f"mysql+aiomysql://{db_config.MYSQL_USER}:{db_config.MYSQL_PASSWORD}@{db_config.MYSQL_HOST}"
            f":{db_config.MYSQL_PORT}/{db_config.MYSQL_DB}",
            echo=False,
            pool_pre_ping=True,
            pool_recycle=28000
        )

        self.async_session_local = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
        )
        logger.info("Connected to the MySQL database.")

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        async_session = self.async_session_local()
        try:
            yield async_session
        finally:
            await async_session.close()

    async def close(self):
        await self.engine.dispose()
