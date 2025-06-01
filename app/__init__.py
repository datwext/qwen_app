import logging
from .logger import setup_logger

# Инициализация корневого логгера
logger = setup_logger()

# Можно также здесь инициализировать другие общие зависимости
__version__ = "1.0.0"

def init_app():
    """Функция для инициализации приложения (если понадобится)."""
    logger.info("Приложение инициализировано")