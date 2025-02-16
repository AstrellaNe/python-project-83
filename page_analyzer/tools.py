# tools.py
from urllib.parse import urlparse, urlunparse
from functools import wraps
from flask import flash, redirect, url_for
from page_analyzer.db_connection import get_connection


def use_db_connection(func):
    """Декоратор для автоматического подключения и закрытия базы данных."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = get_connection()
        if not conn:
            flash('Ошибка подключения к базе данных', 'error')
            return redirect(url_for('index'))
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper


def normalize_url(url):
    url = url.strip()  # Убираем лишние пробелы
    parsed_url = urlparse(url)

    # Если схема отсутствует и URL не начинается с '//' или схемы
    if not parsed_url.scheme and not url.startswith('//'):
        url = f'//{url}'  # Добавляем '//' в начало для правильного парсинга

    # Повторный парсинг после добавления '//' (если нужно)
    parsed_url = urlparse(url)

    # Если схема отсутствует, добавляем https
    if not parsed_url.scheme:
        parsed_url = parsed_url._replace(scheme="https")

    return urlunparse(parsed_url)
