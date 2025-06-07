# page_analyzer/validation.py

import validators
from page_analyzer.db import get_id_by_name


def is_valid_url(url: str) -> bool:
    """
    Проверяет корректность URL и длину не более 255 символов.
    """
    return bool(validators.url(url)) and len(url) <= 255


def check_url_not_exists(conn, url: str) -> bool:
    """
    Возвращает True, если в таблице urls нет записи с таким URL.
    """
    return get_id_by_name(conn, url) is None


def is_valid_id(conn, url_id: int) -> bool:
    """
    Проверяет, что запись с таким id существует в таблице urls.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM urls WHERE id = %s;",
            (url_id,)
        )
        return cur.fetchone() is not None
