import pika
from app.config import RABBITMQ_URL
import logging
from app.logger import setup_logger

logger = setup_logger(__name__)


def create_exchanges():
    try:
        # Подключение к RabbitMQ
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()

        # Создание обменника 'files'
        channel.exchange_declare(
            exchange='files',
            exchange_type='direct',
            durable=True
        )
        logger.info("Обменник 'files' создан или уже существует")

        # Создание обменника 'data'
        channel.exchange_declare(
            exchange='data',
            exchange_type='direct',
            durable=True
        )
        logger.info("Обменник 'data' создан или уже существует")

        # Закрытие соединения
        connection.close()

    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Ошибка подключения к RabbitMQ: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при создании обменников: {e}")