# page_analyzer/tools.py

from functools import wraps
from urllib.parse import urlparse
from page_analyzer.db import get_db_conn


def use_db_connection(view_func):
    """
    Декоратор для передачи соединения с БД в представление.
    Логика открытия/фиксации/закрытия соединения полностью
    реализована в контекст-менеджере get_db_conn().
    """
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        with get_db_conn() as conn:
            return view_func(conn, *args, **kwargs)
    return wrapped


def normalize_url(raw_url: str) -> str:
    """
    Нормализует URL: оставляет только схему и сетевой адрес.
    Например, https://site.ru/page → https://site.ru
    """
    parsed = urlparse(raw_url)
    scheme = parsed.scheme or "http"
    netloc = parsed.netloc
    return f"{scheme}://{netloc}"
