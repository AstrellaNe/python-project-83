import logging
import psycopg2
from contextlib import contextmanager
from flask import current_app

# ─── Контекст-менеджер для работы с соединением ───────────────────────────────


@contextmanager
def get_db_conn():
    """
    Открывает соединение с БД, даёт его пользователю и
    автоматически делает commit/rollback и закрывает.
    """
    dsn = current_app.config["DATABASE_URL"]
    conn = None
    try:
        conn = psycopg2.connect(dsn)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"[DB ERROR] {e}")
        raise
    finally:
        if conn:
            conn.close()

# ─── Функции для работы с таблицей urls ───────────────────────────────────────


def insert_url(conn, name: str) -> int:
    """
    Вставляет новый URL и возвращает его id.
    """
    with conn.cursor() as cur:
        cur.execute(
            (
                "INSERT INTO urls (name, created_at) "
                "VALUES (%s, NOW()) "
                "RETURNING id;"
            ),
            (name,),
        )
        return cur.fetchone()[0]


def get_all_urls(conn) -> list[tuple]:
    """
    Возвращает список всех URL-ов: [(id, name, created_at), ...]
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
              u.id,
              u.name,
              u.created_at,
              (SELECT MAX(c.created_at) FROM url_checks c WHERE c.url_id = u.id)
                AS last_checked_at,
              (SELECT c2.status_code
                 FROM url_checks c2
                WHERE c2.url_id = u.id
                ORDER BY c2.created_at DESC
                LIMIT 1) AS status_code
            FROM urls u
            ORDER BY u.id;
        """)
        rows = cur.fetchall()

    result = []
    for id_, name, created_at, last_checked_at, status_code in rows:
        result.append({
            "id": id_,
            "name": name,
            "created_at": created_at,
            "last_checked_at": last_checked_at,
            "status_code": (
                str(status_code) if status_code is not None else None
            ),
        })
    return result


def get_id_by_name(conn, name: str) -> int | None:
    """
    Ищет запись по name и возвращает её id или None, если нет.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM urls WHERE name = %s;", (name,))
        row = cur.fetchone()
        return row[0] if row else None


def get_name_by_id(conn, url_id: int) -> str | None:
    """
    Ищет запись по id и возвращает её name или None, если нет.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM urls WHERE id = %s;", (url_id,))
        row = cur.fetchone()
        return row[0] if row else None


# ─── Функции для работы с таблицей url_checks ─────────────────────────────────

def insert_check(
    conn,
    url_id: int,
    status_code: int,
    h1: str | None,
    title: str | None,
    description: str | None,
) -> None:
    """
    Сохраняет результат проверки страницы.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO url_checks
                (url_id, status_code, h1, title, description, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW());
            """,
            (url_id, status_code, h1, title, description),
        )


def get_url_with_checks(conn, url_id: int) -> tuple[tuple, list[tuple]]:
    """
    Возвращает данные по URL и все связанные с ним проверки:
    (
      (url_id, name, created_at),
      [
        (check_id, status_code, h1, title, description, created_at),
        ...
      ]
    )
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, created_at FROM urls WHERE id = %s;",
            (url_id,),
        )
        url_data = cur.fetchone()

        cur.execute(
            """
            SELECT id, status_code, h1, title, description, created_at
            FROM url_checks
            WHERE url_id = %s
            ORDER BY created_at DESC;
            """,
            (url_id,),
        )
        checks = cur.fetchall()

    return url_data, checks
