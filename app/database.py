import psycopg2
from app.config import DB_CONFIG


def get_active_organizations():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT org_id FROM ucdb.information.organization WHERE is_active = TRUE")
    return [row[0] for row in cur.fetchall()]


def get_jwt_token(org_id):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT token FROM ucdb.information.tokens WHERE org_id = %s", (org_id,))
    result = cur.fetchone()
    return result[0] if result else None


def get_current_reports():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT report_id FROM wildberries.reports.realization_weekly_list")
    return set(row[0] for row in cur.fetchall())


def add_new_report(report_id):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("INSERT INTO wildberries.reports.realization_weekly_list (report_id) VALUES (%s)", (report_id,))
    conn.commit()


def update_report_status(report_id, status="downloaded"):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("UPDATE wildberries.reports.realization_weekly_list SET status = %s WHERE report_id = %s",
                (status, report_id))
    conn.commit()