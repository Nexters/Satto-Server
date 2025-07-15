import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler

from src.common.logger.handlers import AsyncQueueHandler


async def log_processor(log_queue: asyncio.Queue):
    """
    비동기 로그 처리기 - 큐에서 로그 레코드를 받아 각종 핸들러로 처리

    - 콘솔 출력 (StreamHandler)
    - 파일 저장 (TimedRotatingFileHandler) - 자정마다 로테이션, 60일 보관
    """

    # 로깅 포맷 설정
    formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] %(levelname)s - %(message)s"
    )

    # 파일 핸들러 생성
    file_handler = TimedRotatingFileHandler(
        f"/data/logs/app/app.log", when="midnight", interval=1, backupCount=60
    )
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y-%m-%d"

    # 스트림 핸들러 생성
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    while True:
        record = await log_queue.get()
        if record is None:
            break

        stream_handler.handle(record)
        file_handler.handle(record)


def configure_logger() -> tuple[logging.Logger, asyncio.Queue]:
    """
    비동기 로깅을 위한 핸들러와 로거 설정
    """
    log_queue = asyncio.Queue()

    loggers = {  # 필요 로거 정의
        "apscheduler": logging.getLogger("apscheduler"),
        "uvicorn": logging.getLogger("uvicorn"),
        "uvicorn.access": logging.getLogger("uvicorn.access"),
    }

    loggers["apscheduler"].setLevel(logging.DEBUG)

    for name, logger in loggers.items():
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    # 설정된 로거에 비동기 핸들러 추가 및 전파 비활성화
    async_queue_handler = AsyncQueueHandler(log_queue)
    for name, logger in loggers.items():
        logger.addHandler(async_queue_handler)
        logger.propagate = False

    return loggers["uvicorn"], log_queue
