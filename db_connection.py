import psycopg2
import os
from dotenv import load_dotenv


# Загрузка переменных окружения
load_dotenv()


# Получение URL базы данных из переменной окружения
DATABASE_URL = os.getenv('DATABASE_URL')


# Функция для установки соединения с базой данных
def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


# Функция для добавления URL в базу данных
def add_url(name):
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO urls (name) VALUES (%s) "
                    "ON CONFLICT (name) DO NOTHING;",
                    (name,)
                )
                conn.commit()
                print("URL успешно добавлен")
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении URL: {e}")
        finally:
            conn.close()


# Функция для получения всех URL
def get_all_urls():
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM urls ORDER BY created_at DESC;")
                return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка при получении данных: {e}")
        finally:
            conn.close()
