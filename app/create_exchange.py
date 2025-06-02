import pika
from config import RABBITMQ_URL
from app.logger import setup_logger
def create_exchanges():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    # Создаём обменник типа 'direct' (можно выбрать другой тип при необходимости)
    channel.exchange_declare(
        exchange='files',
        exchange_type='direct',  # тип обменника
        durable=True              # сохраняется после перезапуска
    )
    channel.exchange_declare(
        exchange='data',
        exchange_type='direct',  # тип обменника
        durable=True              # сохраняется после перезапуска
    )

    print("Обменник 'files' создан или уже существует")

    connection.close()