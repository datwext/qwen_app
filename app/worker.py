import pika
import requests
import base64
import rarfile
import openpyxl
import io
import logging
from config import LOG_FILE
from database import update_report_status, get_jwt_token, get_active_organizations
from database import get_current_reports

logging.basicConfig(filename=LOG_FILE, level=logging.INFO)


def process_realization_excel(ch, method, properties, body):
    report_id = body.decode()
    try:
        org_id = 1  # Example: можно передать в сообщении или определить по report_id
        jwt = get_jwt_token(org_id)
        if not jwt:
            logging.warning(f"No JWT for org {org_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        headers = {"Authorization": f"Bearer {jwt}"}
        response = requests.get(f"{config.API_URL}/download/{report_id}", headers=headers)

        if response.status_code == 200:
            b64_data = response.json()['data']
            rar_data = base64.b64decode(b64_data)

            # Extract RAR and XLSX
            with rarfile.RarFile(io.BytesIO(rar_data)) as rf:
                xlsx_file = rf.read('0.xlsx')
                wb = openpyxl.load_workbook(io.BytesIO(xlsx_file))
                ws = wb.active
                for row in ws.iter_rows(min_row=2):  # Skip header
                    values = [cell.value for cell in row]
                    # Save into DB here
                    print(values)  # Replace with actual DB insert

            # Enqueue conversion task
            connection = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
            channel = connection.channel()
            channel.queue_declare(queue='files.xls_to_excel')
            channel.basic_publish(
                exchange='',
                routing_key='files.xls_to_excel',
                body=f"{report_id}|wildberries.reports.realization_weekly"
            )
            connection.close()

            update_report_status(report_id)
            logging.info(f"Processed report {report_id}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.error(f"Error processing {report_id}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_worker():
    connection = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='files.realization_excel')

    channel.basic_consume(queue='files.realization_excel', on_message_callback=process_realization_excel)
    logging.info("Worker started...")
    channel.start_consuming()