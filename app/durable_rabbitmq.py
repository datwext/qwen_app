import socket
import time
from app.logger import setup_logger

logger = setup_logger(__name__)

def wait_for_rabbitmq(host="rabbitmq", port=5672, timeout=60, retry_interval=5):
    logger.info(f"Ожидание доступности RabbitMQ по адресу {host}:{port}...")
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            with socket.create_connection((host, port), timeout=10):
                logger.info("RabbitMQ доступен!")
                return True
        except OSError as e:
            logger.warning(f"RabbitMQ недоступен: {e}. Жду {retry_interval} секунд...")
            time.sleep(retry_interval)
    logger.error("Превышено время ожидания RabbitMQ.")
    return False