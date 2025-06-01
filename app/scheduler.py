import schedule
import time
from datetime import datetime

from app.database import get_active_organizations
from app.logger import setup_logger

logger = setup_logger(__name__)


def fetch_and_queue_reports():
    """Пример задачи, которая выполняется по расписанию."""
    logger.info("Начало выполнения задачи по получению отчётов")

    try:
        organizations = get_active_organizations()
        if not organizations:
            logger.warning("Нет активных организаций для обработки")
        else:
            for org_id in organizations:
                logger.info(f"Обработка организации: {org_id}")

        logger.info("Задача завершена")
    except Exception as e:
        logger.error(f"Ошибка выполнения задачи: {e}")


def run_scheduler():
    """Функция запуска планировщика."""
    try:
        with open("cron.cfg") as f:
            line = f.readline().strip()
            minute, hour, day, month, dow = line.split()

            # Если используется cron-формат (например, */5 * * * *)
            if '*' in minute or '*' in hour:
                minute_interval = int(minute.replace('*/', ''))
                logger.info(f"Запуск каждые {minute_interval} минут")
                schedule.every(minute_interval).minutes.do(fetch_and_queue_reports)
            else:
                logger.info(f"Запуск каждый день в {hour}:{minute}")
                schedule.every().day.at(f"{hour}:{minute}").do(fetch_and_queue_reports)

    except Exception as e:
        logger.error(f"Ошибка чтения cron.cfg: {e}")
        return

    logger.info("Планировщик запущен. Ожидание задач...")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    run_scheduler()