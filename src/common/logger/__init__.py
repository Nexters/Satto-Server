import asyncio

from .initializer import configure_logger, log_processor

logger, log_queue = configure_logger()


async def start_logging():
    """로깅 시스템 초기화"""
    log_processor_task = asyncio.create_task(log_processor(log_queue))
    return log_processor_task
