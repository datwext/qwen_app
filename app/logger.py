import logging
import sys
from app.config import LOG_FILE  # Исправленный импорт


def setup_logger(name=__name__, level=logging.INFO):
    """
    Настраивает логгер с выводом в консоль и файл.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Логгирование в файл
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)

        # Логгирование в консоль
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger