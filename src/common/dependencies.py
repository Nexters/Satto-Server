from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.fortune.application.service import FortuneService
from src.fortune.domain.interfaces import IFortuneRepository
from src.fortune.infrastructure.repository import FortuneRepository
from src.lotto.application.service import LottoService
from src.lotto.domain.interfaces import ILottoRepository
from src.lotto.infrastructure.repository import LottoRepository
from src.lotto_stores.application.service import LottoStoreService
from src.lotto_stores.domain.interfaces import ILottoStoreRepository
from src.lotto_stores.infrastructure.repository import LottoStoreRepository
from src.users.application.service import UserService
from src.users.domain.interfaces import IUserRepository
from src.users.infrastructure.repository import UserRepository
from src.atm.application.service import AtmService
from src.atm.domain.interfaces import IAtmRepository
from src.atm.infrastructure.repository import AtmRepository


def get_db_session(request: Request) -> AsyncSession:
    """DB 세션 의존성 주입 함수"""
    return request.state.db_session


def get_lotto_service(
    session: AsyncSession = Depends(get_db_session),
) -> LottoService:
    """로또 서비스 의존성 주입 함수"""
    lotto_repository: ILottoRepository = LottoRepository(session=session)
    user_repository: IUserRepository = UserRepository(session=session)
    return LottoService(
        lotto_repository=lotto_repository,
        user_repository=user_repository,
    )


def get_fortune_service(
    session: AsyncSession = Depends(get_db_session),
) -> FortuneService:
    """운세 서비스 의존성 주입 함수"""
    fortune_repository: IFortuneRepository = FortuneRepository(session=session)
    user_repository: IUserRepository = UserRepository(session=session)
    return FortuneService(
        fortune_repository=fortune_repository,
        user_repository=user_repository,
    )


def get_user_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserService:
    """사용자 서비스 의존성 주입 함수"""
    user_repository: IUserRepository = UserRepository(session=session)
    return UserService(user_repository=user_repository)


def get_lotto_store_service(
    session: AsyncSession = Depends(get_db_session),
) -> LottoStoreService:
    """로또 판매점 서비스 의존성 주입 함수"""
    store_repository: ILottoStoreRepository = LottoStoreRepository(
        session=session
    )
    return LottoStoreService(store_repository=store_repository)



def get_atm_service(
    session: AsyncSession = Depends(get_db_session),
) -> AtmService:
    """ATM 서비스 의존성 주입 함수"""
    atm_repository: IAtmRepository = AtmRepository(
        session=session
    )
    return AtmService(atm_repository=atm_repository)