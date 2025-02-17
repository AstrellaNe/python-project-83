import os
import datetime
import psycopg2
import requests
import validators
from bs4 import BeautifulSoup
from flask import (Flask, request, redirect, flash,
                   render_template, url_for)
from page_analyzer.db_connection import (insert_url, get_all_urls,
                                         url_exists, insert_check,
                                         get_url_with_checks)
from page_analyzer.tools import normalize_url, use_db_connection
from dotenv import load_dotenv


# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d'):
    if isinstance(value, datetime.datetime):
        return value.strftime(format)
    return value


# Главная страница (Index)
@app.route('/')
@use_db_connection
def index(conn):
    return render_template('index.html')


# Страница со списком всех сайтов (urls.html)
@app.route('/urls')
@use_db_connection
def urls(conn):
    urls = get_all_urls(conn)
    return render_template('urls.html', urls=urls)


# Добавление нового URL в БД
@app.route('/urls', methods=['POST'])
@use_db_connection
def add_url(conn):
    input_url = request.form.get('url')
    normalized_url = normalize_url(input_url)

    if not validators.url(normalized_url):
        flash('Некорректный URL', 'danger')
        return redirect(url_for('index'))

    if url_exists(conn, normalized_url):
        flash('Страница уже существует', 'info')
        return redirect(url_for('urls'))

    url_id = insert_url(conn, normalized_url)
    if url_id:
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('url_details', id=url_id))

    flash('Ошибка: URL уже существует.', 'warning')
    return redirect(url_for('urls'))


# Детальная страница сайта (url_details.html)
@app.route('/urls/<int:id>')
@use_db_connection
def url_details(conn, id):
    url, checks = get_url_with_checks(conn, id)

    if not url:
        flash('Страница не найдена', 'danger')
        return redirect(url_for('urls'))

    return render_template('url_details.html', url=url, checks=checks)


# Разбиваем `check_url()` на две функции, чтобы уменьшить сложность
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
        flash(f"Ошибка запроса: {e}", "danger")
        return None, None, None, None


# Запуск проверки сайта
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
            flash("Проверка успешно проведена", "success")

    return redirect(url_for('url_details', id=id))


# Удаление URL
@app.route('/urls/delete/<int:id>', methods=['POST'])
@use_db_connection
def delete_url(conn, id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM urls WHERE id = %s;", (id,))
            conn.commit()
            flash('Страница успешно удалена', 'success')

    except psycopg2.Error as e:
        flash(f"Ошибка при удалении: {e}", 'danger')

    return redirect(url_for('urls'))


if __name__ == '__main__':
    app.run(debug=True)
