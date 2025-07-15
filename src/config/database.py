from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.config import db_config


class Mysql:
    def __init__(self, config: db_config) -> None:
        self.config = config

        self.engine = create_async_engine(
            "mysql+aiomysql://"
            + config.MYSQL_USER
            + ":"
            + config.MYSQL_PASSWORD
            + "@"
            + config.MYSQL_HOST
            + ":"
            + config.MYSQL_PORT
            + "/"
            + config.MYSQL_DB,
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

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        async_session = self.async_session_local()
        try:
            yield async_session
        finally:
            await async_session.close()

    async def close(self):
        await self.engine.dispose()
