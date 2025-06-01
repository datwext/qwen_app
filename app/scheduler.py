import pika
from config import RABBITMQ_URL

import schedule
import time
from datetime import datetime

from app.database import get_active_organizations
from app.logger import setup_logger

logger = setup_logger(__name__)


def fetch_and_queue_reports():
    logger.info("Начало выполнения задачи по получению отчётов")

    try:
        organizations = get_active_organizations()
        if not organizations:
            logger.warning("Нет активных организаций для обработки")
        else:
            for org_id in organizations:
                logger.info(f"Обработка организации: {org_id}")
                send_to_rabbitmq('files.realization_excel', f"task_for_org_{org_id}")

        logger.info("Задача завершена")
    except Exception as e:
        logger.error(f"Ошибка выполнения задачи: {e}")

def send_to_rabbitmq(queue_name, body):
    """Отправляет сообщение в очередь RabbitMQ."""
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=str(body),
            properties=pika.BasicProperties(delivery_mode=2)  # Устойчивое сообщение
        )
        connection.close()
        logger.info(f"Сообщение отправлено в очередь {queue_name}: {body}")
    except Exception as e:
        logger.error(f"Ошибка при отправке в очередь: {e}")

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