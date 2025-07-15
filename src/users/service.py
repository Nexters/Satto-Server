from fastapi import Depends

from src.users.repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository = Depends()):
        self.repository = user_repository

    async def test(self):
        return await self.repository.test()
