import logging
from .logger import setup_logger
from .config import DB_CONFIG
import psycopg2

logger = setup_logger(__name__)


def init_db():
    """Создаёт схемы и таблицы, если их нет."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Схемы
        cur.execute("CREATE SCHEMA IF NOT EXISTS information;")
        cur.execute("CREATE SCHEMA IF NOT EXISTS reports;")

        # Таблицы
        cur.execute("""
            CREATE TABLE IF NOT EXISTS information.organization (
                org_id UUID PRIMARY KEY,
                is_active BOOLEAN NOT NULL DEFAULT TRUE
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS information.tokens (
                token_id SERIAL PRIMARY KEY,
                org_id UUID REFERENCES information.organization(org_id),
                token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS reports.realization_weekly_list (
                report_id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'pending',
                downloaded_at TIMESTAMP
            );
        """)

        conn.commit()
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()