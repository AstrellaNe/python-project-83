# db_connection.py
import os
import psycopg2
import os
from dotenv import load_dotenv


# Загрузка переменных окружения
load_dotenv()


# Получение URL базы данных из переменной окружения
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("❌ Ошибка: DATABASE_URL не установлен! Проверь переменные окружения на Render.")


# Функция для установки соединения с базой данных
def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Подключение к БД успешно!")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return None


# Функция для установки соединения с базой данных
def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


# Функция для добавления URL в базу данных
def insert_url(conn, name):
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO urls (name) VALUES (%s) "
            "ON CONFLICT (name) DO NOTHING;",
            (name,)
        )
        conn.commit()


# Функция для получения всех URL
def get_all_urls():
    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM urls ORDER BY created_at DESC;")
        return cursor.fetchall()


# Проверяет, существует ли URL в базе данных
def url_exists(conn, name):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM urls WHERE name = %s;",
            (name,)
        )
        return cursor.fetchone() is not None
