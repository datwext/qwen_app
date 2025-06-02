import pika
import time
from config import RABBITMQ_URL
import logging
from app.logger import setup_logger

logger = setup_logger(__name__)


def create_exchanges(max_retries=10, retry_delay=5):
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Попытка подключения к RabbitMQ (попытка {attempt}/{max_retries})...")
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()

            # Создание обменников
            channel.exchange_declare(exchange='files', exchange_type='direct', durable=True)
            channel.exchange_declare(exchange='data', exchange_type='direct', durable=True)

            logger.info("Обменники 'files' и 'data' созданы или уже существуют")
            connection.close()
            return  # Успешное выполнение

        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Ошибка подключения к RabbitMQ: {e}")
            if attempt < max_retries:
                logger.info(f"Ждём {retry_delay} секунд перед следующей попыткой...")
                time.sleep(retry_delay)
            else:
                logger.error("Достигнуто максимальное количество попыток подключения к RabbitMQ.")
                raise
        except Exception as e:
            logger.error(f"Неизвестная ошибка при создании обменников: {e}")
            raise