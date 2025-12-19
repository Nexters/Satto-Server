from src.common.logger import logger
from src.config.config import db_config
from src.config.database import Mysql
from src.lotto.application.service import LottoService
from src.lotto.infrastructure.repository import LottoRepository
from src.users.infrastructure.repository import UserRepository


async def update_next_lotto_draw():
    """다음 회차 로또 데이터를 동행복권 API에서 가져와서 데이터베이스에 저장합니다."""
    db = Mysql(db_config)

    try:
        async with db.session() as session:
            lotto_repository = LottoRepository(session)
            user_repository = UserRepository(session)
            lotto_service = LottoService(
                lotto_repository=lotto_repository,
                user_repository=user_repository,
            )
            success = await lotto_service.update_next_lotto_draw()
            await session.commit()
            if success:
                logger.info("로또 데이터 업데이트가 성공적으로 완료되었습니다.")
            else:
                logger.warning("로또 데이터 업데이트가 실패했습니다.")

    except Exception as e:
        logger.error(f"로또 데이터 업데이트 중 오류 발생: {e}")
    finally:
        await db.close()
