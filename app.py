# app.py
import psycopg2
import os
import datetime
from flask import Flask, request, redirect, flash, render_template, url_for
from db_connection import insert_url, get_all_urls, url_exists, insert_check
import validators
from tools import normalize_url, use_db_connection  # Импортируем декоратор
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
    urls = get_all_urls(conn)  # ← Передаём conn, потому что @ его добавляет
    return render_template('index.html', urls=urls)


@app.route('/add-url', methods=['POST'])
@use_db_connection
def add_url(conn):
    input_url = request.form.get('url')
    print(f"Input URL: {input_url}")  # Логируем входной URL

    normalized_url = normalize_url(input_url)
    print(f"Normalized URL: {normalized_url}")  # Логируем нормализованный URL

    if not validators.url(normalized_url):
        flash('Некорректный URL, проверьте формат ввода URL', 'error')
        print("Validation failed.")  # Логируем провал валидации
        return redirect(url_for('index'))

    # Проверяем, существует ли уже URL
    if url_exists(conn, normalized_url):
        flash('Этот URL уже существует в базе данных', 'info')
        print("URL already exists in the database.")
        # Логируем, что URL уже есть
        return redirect(url_for('index'))

    try:
        insert_url(conn, normalized_url)  # Вызываем функцию для добавления URL
        flash('URL успешно добавлен', 'success')
    except Exception as e:
        flash(f'Ошибка при добавлении URL: {e}', 'error')
        print(f"Database error: {e}")  # Логируем ошибки базы данных

    return redirect(url_for('index'))


@app.route('/urls/<int:id>')
@use_db_connection
def show_url(conn, id):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM urls WHERE id = %s;", (id,)
            )
            url = cursor.fetchone()

            if url:
                cursor.execute(
                    """SELECT id, created_at FROM url_checks
                       WHERE url_id = %s ORDER BY created_at DESC;""",
                    (id,)
                )
                checks = cursor.fetchall()
                print(f"🔥 Загруженные проверки: {checks}")

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
            flash('URL успешно удален', 'success')
    except psycopg2.Error as e:
        flash(f"Ошибка при удалении URL: {e}", 'error')
    return redirect(url_for('index'))


# при нажатии кнопки будет создаваться новая проверка
@app.route('/urls/<int:id>/checks', methods=['POST'])
@use_db_connection
def check_url(conn, id):
    try:
        insert_check(conn, id)
        flash("Проверка добавлена!", "success")
    except psycopg2.Error as e:
        flash(f"Ошибка при добавлении проверки: {e}", "danger")

    return redirect(url_for('show_url', id=id))


if __name__ == '__main__':
    app.run(debug=True)
