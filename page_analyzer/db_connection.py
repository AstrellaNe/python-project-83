import os
import psycopg2
from dotenv import load_dotenv


# Загружаем переменные окружения
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise ValueError("❌ Ошибка: DATABASE_URL не установлен!")


# Функция для установки соединения с базой данных
def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Успешное подключение к БД!")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None


# Функция для добавления URL в базу данных
def insert_url(conn, name):
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO urls (name)
               VALUES (%s)
               ON CONFLICT (name) DO NOTHING
               RETURNING id;""",
            (name,)
        )
        url_id = cursor.fetchone()
        conn.commit()
        return url_id[0] if url_id else None
    

def insert_check(conn, url_id, status_code, h1, title, description):
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO url_checks (url_id, status_code, h1, title, description)
               VALUES (%s, %s, %s, %s, %s)
               RETURNING id, created_at;""",
            (url_id, status_code, h1, title, description)
        )
        check = cursor.fetchone()
        conn.commit()
        return check


# Функция для получения всех URL
def get_all_urls(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT urls.id, urls.name, urls.created_at,
                      (SELECT created_at FROM url_checks
                       WHERE url_checks.url_id = urls.id
                       ORDER BY created_at DESC
                       LIMIT 1) AS last_status
               FROM urls
               ORDER BY urls.created_at DESC;"""
        )
        return cursor.fetchall()


# Проверяет, существует ли URL в базе данных
def url_exists(conn, name):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM urls WHERE name = %s;",
            (name,)
        )
        return cursor.fetchone() is not None


# Получение данных о сайте и его проверках
def get_url_with_checks(conn, url_id):
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT id, name, created_at
               FROM urls
               WHERE id = %s;""",
            (url_id,)
        )
        url = cursor.fetchone()

        cursor.execute(
            """SELECT id, status_code, h1, title, description, created_at
               FROM url_checks
               WHERE url_id = %s
               ORDER BY created_at DESC;""",
            (url_id,)
        )
        checks = cursor.fetchall()

    return url, checks
