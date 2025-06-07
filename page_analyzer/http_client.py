# page_analyzer/http_client.py

import requests
from bs4 import BeautifulSoup


class FetchError(Exception):
    """Исключение при ошибках при получении или парсинге страницы."""


def fetch_url_data(url: str) -> tuple[int, str | None, str | None, str | None]:
    """
    Выполняет GET-запрос к указанному URL и возвращает кортеж:
    (status_code, h1, title, description).

    При таймауте бросает FetchError("timeout"),
    при любых других ошибках запросов — FetchError("request_error").
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
    except requests.Timeout as e:
        raise FetchError("timeout") from e
    except requests.RequestException as e:
        raise FetchError("request_error") from e

    soup = BeautifulSoup(response.text, "html.parser")
    status_code = response.status_code

    h1 = soup.h1.text.strip() if soup.h1 else None
    title = soup.title.text.strip() if soup.title else None
    meta = soup.find("meta", attrs={"name": "description"})
    description = (
        meta["content"].strip()
        if meta and meta.get("content")
        else None
    )

    return status_code, h1, title, description
