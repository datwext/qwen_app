import schedule
import time
import logging

from app import config
from config import LOG_FILE
from database import get_active_organizations, get_jwt_token
import pika
import requests
from database import get_current_reports, add_new_report

logging.basicConfig(filename=LOG_FILE, level=logging.INFO)


def fetch_and_queue_reports():
    organizations = get_active_organizations()
    for org_id in organizations:
        jwt = get_jwt_token(org_id)
        if not jwt:
            logging.warning(f"No JWT found for org {org_id}")
            continue

        headers = {"Authorization": f"Bearer {jwt}"}
        response = requests.get(f"{config.API_URL}/list", headers=headers)

        if response.status_code == 200:
            current_reports = get_current_reports()
            remote_reports = set(response.json())
            new_reports = remote_reports - current_reports

            for report_id in new_reports:
                add_new_report(report_id)

                # Publish to queue
                connection = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
                channel = connection.channel()
                channel.queue_declare(queue='files.realization_excel')
                channel.basic_publish(
                    exchange='',
                    routing_key='files.realization_excel',
                    body=str(report_id)
                )
                connection.close()
                logging.info(f"Queued report {report_id} for download")
        else:
            logging.error(f"Failed to fetch reports for org {org_id}, status {response.status_code}")

# Schedule job
def run_scheduler():
    from datetime import datetime
    with open("cron.cfg") as f:
        cron_line = f.readline().strip()
        minute, hour, day, month, dow = cron_line.split()
        schedule.every().day.at(f"{hour}:{minute}").do(fetch_and_queue_reports)

    while True:
        schedule.run_pending()
        time.sleep(60)