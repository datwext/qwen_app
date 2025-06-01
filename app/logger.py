import logging
import sys
from config import LOG_FILE

def setup_logger(name=__name__, level=logging.INFO):
    """
    Настройка логгера с выводом в консоль и записью в файл.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Предотвращаем дублирование логов при повторном вызове
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