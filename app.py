import psycopg2
import os
import datetime
from flask import Flask, request, redirect, flash, render_template, url_for
from db_connection import add_url, get_all_urls, get_connection
import validators  # Библиотека для валидации URL

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


# Фильтр для форматирования даты и времени без тысячных сек
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, datetime.datetime):
        return value.strftime(format)
    return value


@app.route('/')
def index():
    urls = get_all_urls()
    return render_template('index.html', urls=urls)


@app.route('/add-url', methods=['POST'])
def add_url_route():
    url = request.form['url']

    # Проверка на корректность URL
    if not url or not validators.url(url) or len(url) > 255:
        flash('Некорректный URL', 'error')
        return redirect(url_for('index'))

    # Проверка на уникальность URL
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM urls WHERE name = %s;", (url,))
                existing_url = cursor.fetchone()
                if existing_url:
                    flash('Этот URL уже существует.', 'error')
                    return redirect(url_for('index'))
                add_url(url)
                flash('URL успешно добавлен', 'success')
        except psycopg2.Error as e:
            flash(f"Ошибка при добавлении URL: {e}", 'error')
        finally:
            conn.close()

    return redirect(url_for('index'))


@app.route('/urls/<int:id>')
def show_url(id):
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM urls WHERE id = %s;", (id,))
                url = cursor.fetchone()
                if url:
                    return render_template('url_details.html', url=url)
                else:
                    flash('URL не найден', 'error')
                    return redirect(url_for('index'))
        except psycopg2.Error as e:
            flash(f"Ошибка при получении данных: {e}", 'error')
        finally:
            conn.close()


@app.route('/urls/delete/<int:id>', methods=['POST'])
def delete_url(id):
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM urls WHERE id = %s;", (id,))
                conn.commit()
                flash('URL успешно удален', 'success')
        except psycopg2.Error as e:
            flash(f"Ошибка при удалении URL: {e}", 'error')
        finally:
            conn.close()
    return redirect(url_for('index'))
