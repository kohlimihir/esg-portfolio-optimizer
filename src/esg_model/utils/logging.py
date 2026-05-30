import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <7}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
)

__all__ = ["logger"]
