import schedule
import time
import requests
from datetime import datetime

from app.database import get_active_organizations, get_jwt_token, get_current_reports, add_new_report
from app.logger import setup_logger
from app.config import API_URL, RABBITMQ_URL
import pika

logger = setup_logger(__name__)


def fetch_and_queue_reports():
    logger.info("Начало выполнения задачи по получению отчётов")

    organizations = get_active_organizations()

    for org_id in organizations:
        jwt = get_jwt_token(org_id)
        if not jwt:
            logger.warning(f"Токен не найден для организации {org_id}")
            continue

        headers = {"Authorization": f"Bearer {jwt}"}
        response = requests.get(f"{API_URL}/list", headers=headers)

        if response.status_code == 200:
            remote_reports = set(response.json())
            current_reports = get_current_reports()
            new_reports = remote_reports - current_reports

            for report_id in new_reports:
                add_new_report(report_id)

                try:
                    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
                    channel = connection.channel()
                    channel.queue_declare(queue='files.realization_excel')
                    channel.basic_publish(
                        exchange='',
                        routing_key='files.realization_excel',
                        body=str(report_id)
                    )
                    connection.close()
                    logger.info(f"Отчёт {report_id} добавлен в очередь")
                except Exception as e:
                    logger.error(f"Ошибка при отправке в очередь: {e}")
        else:
            logger.error(f"Ошибка получения отчётов для org_id={org_id}, статус {response.status_code}")

    logger.info("Задача завершена")


def run_scheduler():
    from datetime import datetime
    with open("cron.cfg") as f:
        line = f.readline().strip()
        minute, hour, day, month, dow = line.split()
        schedule.every().day.at(f"{hour}:{minute}").do(fetch_and_queue_reports)

    logger.info("Планировщик запущен...")
    while True:
        schedule.run_pending()
        time.sleep(60)