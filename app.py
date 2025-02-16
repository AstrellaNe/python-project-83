# app.py
import os
import datetime
import psycopg2
import requests
import validators
from bs4 import BeautifulSoup
from flask import (Flask, request, redirect, flash,
                   render_template, url_for)
from db_connection import (insert_url, get_all_urls,
                           url_exists, insert_check)

from tools import normalize_url, use_db_connection
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, datetime.datetime):
        return value.strftime(format)
    return value


@app.route('/')
@use_db_connection
def index(conn):
    urls = get_all_urls(conn)
    return render_template('index.html', urls=urls)


@app.route('/add-url', methods=['POST'])
@use_db_connection
def add_url(conn):
    input_url = request.form.get('url')
    print(f"Input URL: {input_url}")

    normalized_url = normalize_url(input_url)
    print(f"Normalized URL: {normalized_url}")

    if not validators.url(normalized_url):
        flash('Некорректный URL', 'error')
        print("Validation failed.")
        return redirect(url_for('index'))

    if url_exists(conn, normalized_url):
        flash('Этот URL уже существует', 'info')
        print("URL already exists.")
        return redirect(url_for('index'))

    try:
        insert_url(conn, normalized_url)
        flash('URL успешно добавлен', 'success')
    except Exception as e:
        flash(f'Ошибка добавления URL: {e}', 'error')
        print(f"Database error: {e}")

    return redirect(url_for('index'))


@app.route('/urls/<int:id>')
@use_db_connection
def show_url(conn, id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM urls WHERE id = %s;", (id,))
            url = cursor.fetchone()

            if url:
                cursor.execute(
                    """SELECT id, status_code, h1,
                              title, description, created_at
                       FROM url_checks WHERE url_id = %s
                       ORDER BY created_at DESC;""",
                    (id,)
                )
                checks = cursor.fetchall()
                print(f"🔥 Отладка.Загруженные проверки: {checks}")

                return render_template(
                    'url_details.html', url=url, checks=checks
                )

            flash('URL не найден', 'error')
            return redirect(url_for('index'))

    except psycopg2.Error as e:
        flash(f"Ошибка при получении данных: {e}", 'error')

    return redirect(url_for('index'))


@app.route('/urls/delete/<int:id>', methods=['POST'])
@use_db_connection
def delete_url(conn, id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM urls WHERE id = %s;", (id,))
            conn.commit()
            flash('URL удалён', 'success')
    except psycopg2.Error as e:
        flash(f"Ошибка при удалении: {e}", 'error')
    return redirect(url_for('index'))


@app.route('/urls/<int:id>/checks', methods=['POST'])
@use_db_connection
def check_url(conn, id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM urls WHERE id = %s;", (id,))
            url = cursor.fetchone()

            if not url:
                flash("URL не найден")
                return redirect(url_for('show_url', id=id))

            url = url[0]
            print(f"🔍 Проверяем URL: {url}")

            try:
                response = requests.get(url, timeout=10, headers={
                    "User-Agent": "Mozilla/5.0"
                })
                response.raise_for_status()
            except requests.RequestException as e:
                flash("""Ошибка при проверке: сайт недоступен
                      или произошла сетевая ошибка.""")
                print(f"❌ Ошибка запроса: {e}")
                return redirect(url_for('show_url', id=id))

            status_code = response.status_code
            soup = BeautifulSoup(response.text, 'html.parser')

            h1 = soup.h1.text.strip() if soup.h1 else None
            title = soup.title.text.strip() if soup.title else None
            meta_tag = soup.find("meta", attrs={"name": "description"})
            description = meta_tag["content"].strip() if meta_tag else None

            print(f"✅ Код: {status_code}, h1: {h1}, title: {title}")

            insert_check(conn, id, status_code, h1, title, description)
            flash("Проверка добавлена!", "success")

    except Exception as e:
        flash("Произошла ошибка при обработке запроса")
        print(f"❌ Ошибка: {e}")

    return redirect(url_for('show_url', id=id))


if __name__ == '__main__':
    app.run(debug=True)
