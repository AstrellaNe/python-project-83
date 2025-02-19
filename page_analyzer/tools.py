# tools.py
from urllib.parse import urlparse
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


def normalize_url(input_url):
    parsed_url = urlparse(input_url)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return normalized_url
