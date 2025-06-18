# app/core/logger.py
import logging
import sys
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # 获取 Loguru 日志等级对应
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(level, record.getMessage())

def init_logger():
    # 先移除默认 handler
    logger.remove()

    # 控制台输出
    logger.add(
        sys.stdout,
        filter=lambda record: record["level"].no < logger.level("ERROR").no,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{level: <8}</level>"
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",
        enqueue=True,
        backtrace=True,
        diagnose=True
    )

    # 高等级日志：ERROR 及以上，输出完整路径
    logger.add(
        sys.stdout,
        level="ERROR",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{level: <8}</level>"
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>\n{file.path}:{line}"
        ),
        enqueue=True,
        backtrace=True,
        diagnose=True
    )

    # 将标准 logging 的 handler 替换为 loguru 的 handler
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 将 uvicorn、fastapi logger 的 handler 清空并阻止传播
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers = [InterceptHandler()]  # 只保留一个 handler
        uv_logger.propagate = False  # 阻止传播给 root logger，防止重复打印
