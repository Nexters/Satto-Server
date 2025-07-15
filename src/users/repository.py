from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.dependencies import get_db_session


class UserRepository:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    def test(self):
        return "test"