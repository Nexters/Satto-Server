from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


def get_db_session(request: Request) -> AsyncSession:
    return request.state.db_session
