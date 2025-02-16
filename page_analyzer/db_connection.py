import os
import psycopg2
import socket
from dotenv import load_dotenv


# Загрузка переменных окружения
load_dotenv()

# Получение URL базы данных из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

if not DATABASE_URL:
    raise ValueError("❌ Ошибка: DATABASE_URL не установлен!")
try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Успешное подключение к БД!")
except psycopg2.OperationalError as e:
    print(f"❌ Ошибка подключения к БД: {e}")
    
if not SECRET_KEY:
    raise ValueError("❌ Ошибка: SECRET_KEY не установлен!")


# Функция для установки соединения с базой данных
def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Успешное подключение к БД!")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None


# Проверяем доступность хоста
host = DATABASE_URL.split("@")[1].split(":")[0]
try:
    print(f"Проверяем доступность хоста: {host}")
    socket.gethostbyname(host)
    print("✅ Хост доступен!")
except socket.gaierror:
    print(f"❌ Ошибка: Хост {host} недоступен!")


# Функция для добавления URL в базу данных
def insert_url(conn, name):
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO urls (name)
               VALUES (%s)
               ON CONFLICT (name) DO NOTHING;""",
            (name,)
        )
        conn.commit()


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


# Функция для записи проверки в базу
def insert_check(conn, url_id, status_code, h1, title, description):
    with conn.cursor() as cursor:
        print(f"🔥 Добавляем проверку: url_id={url_id}, "
              f"status_code={status_code}, h1={h1}")

        cursor.execute(
            """INSERT INTO url_checks (url_id, status_code,
                                       h1, title, description)
               VALUES (%s, %s, %s, %s, %s)
               RETURNING id, created_at;""",
            (url_id, status_code, h1, title, description)
        )
        check = cursor.fetchone()
        conn.commit()
        print(f"✅ Успешно добавлено: {check}")
