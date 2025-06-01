
from .init_db import init_db
from .logger import setup_logger

logger = setup_logger(__name__)

try:
    init_db()
except Exception as e:
    logger.critical(f"Не удалось инициализировать базу данных: {e}")
    raise