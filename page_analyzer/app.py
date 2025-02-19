import os
import datetime
import psycopg2
import requests
import validators
import logging
from bs4 import BeautifulSoup
from flask import Flask, request, redirect, flash, render_template, url_for
from page_analyzer.db_connection import (
    insert_url, get_all_urls, url_exists, insert_check, get_url_with_checks
)
from page_analyzer.tools import normalize_url, use_db_connection
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ Ошибка: DATABASE_URL не установлен!")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')


def get_connection():
    """Функция для установки соединения с базой данных"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Ошибка подключения к БД: {e}")
        return None


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d'):
    if isinstance(value, datetime.datetime):
        return value.strftime(format)
    return value


@app.route('/')
@use_db_connection
def index(conn):
    return render_template('index.html')


@app.route('/urls')
@use_db_connection
def urls(conn):
    urls = get_all_urls(conn)
    return render_template('urls.html', urls=urls)


@app.route('/urls', methods=['POST'])
@use_db_connection
def add_url(conn):
    input_url = request.form.get('url')

    if not input_url:
        flash('URL не может быть пустым', 'danger')
        return render_template('index.html'), 422

    normalized_url = normalize_url(input_url)  # Применяем нормализацию

    if not validators.url(normalized_url):
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422

    if url_exists(conn, normalized_url):
        # Проверяем существование уже нормализованного URL
        flash('Страница уже существует', 'info')
        return redirect(url_for('urls'))
        # Перенаправляем пользователя на список сайтов

    url_id = insert_url(conn, normalized_url)
    # Записываем нормализованный URL в базу
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url_details', id=url_id))


@app.route('/urls/<int:id>')
@use_db_connection
def url_details(conn, id):
    url_data, checks_data = get_url_with_checks(conn, id)

    if not url_data:
        flash('Страница не найдена', 'danger')
        return redirect(url_for('urls'))

    return render_template('url_details.html', url=url_data, checks=checks_data)


def fetch_url_data(url):
    try:
        response = requests.get(url, timeout=10,
                                headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        status_code = response.status_code
        soup = BeautifulSoup(response.text, 'html.parser')

        h1 = soup.h1.text.strip() if soup.h1 else None
        title = soup.title.text.strip() if soup.title else None
        meta_tag = soup.find("meta", attrs={"name": "description"})
        description = meta_tag["content"].strip() if meta_tag else None

        return status_code, h1, title, description

    except requests.Timeout:
        flash("Ошибка: время ожидания запроса истекло", "danger")
        return None, None, None, None

    except requests.RequestException as e:
        flash(f"Произошла ошибка при проверке: {e}", "danger")
        # не было сообщения
        return None, None, None, None


@app.route('/urls/<int:id>/checks', methods=['POST'])
@use_db_connection
def check_url(conn, id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT name FROM urls WHERE id = %s;", (id,))
        url = cursor.fetchone()

        if not url:
            flash("Страница не найдена", "danger")
            return redirect(url_for('url_details', id=id))

        url = url[0]
        status_code, h1, title, description = fetch_url_data(url)

        if status_code:
            insert_check(conn, id, status_code, h1, title, description)
            flash("Страница успешно проверена", "success")
        else:
            flash("Произошла ошибка при проверке", "danger")

    return redirect(url_for('url_details', id=id))


if __name__ == '__main__':
    app.run(debug=True)
