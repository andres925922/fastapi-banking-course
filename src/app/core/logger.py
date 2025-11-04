import os
from loguru import logger

from core.settings import settings

logger.remove()

FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} - "
    "{message}"
)

logger.add(
    os.path.join(settings.LOG_DIR, "debug.log"),
    serialize=True,
    # format=FORMAT,
    level="DEBUG" if settings.ENVIRONMENT == "development" else "INFO",
    filter=lambda record: record["level"].no >= logger.level("WARNING").no,
    rotation="10 MB",
    retention="10 days",
    compression="zip",
)

logger.add(
    sink=os.path.join(settings.LOG_DIR, "error.log"),
    serialize=True,
    # format=FORMAT,
    level="ERROR",
    rotation="10MB",
    retention="30 days",
    compression="zip",
    backtrace=True,
    diagnose=True,
)

def get_logger():
    return logger