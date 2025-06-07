import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, flash

from page_analyzer.tools import use_db_connection, normalize_url
from page_analyzer.validation import (
    is_valid_url, check_url_not_exists, is_valid_id
)
from page_analyzer.db import (
    insert_url,
    get_all_urls,
    get_id_by_name,
    get_name_by_id,
    insert_check,
    get_url_with_checks,
)
from page_analyzer.http_client import fetch_url_data, FetchError

# ─── Настройка приложения ─────────────────────────

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("❌ Ошибка: DATABASE_URL не задана")

app = Flask(__name__)
app.config["DATABASE_URL"] = DATABASE_URL
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")


# ─── Фильтр форматирования даты ───────────────────

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d'):
    return value.strftime(format) if hasattr(value, 'strftime') else value


# ─── Маршруты ──────────────────────────────────────

@app.get("/")
@use_db_connection
def index(conn):
    return render_template("index.html")


@app.get("/urls")
@use_db_connection
def list_urls(conn):
    urls = get_all_urls(conn)
    return render_template("urls.html", urls=urls)


@app.post("/urls")
@use_db_connection
def add_url(conn):
    raw_url = request.form.get("url", "").strip()
    if not raw_url:
        flash("URL не может быть пустым", "danger")
        return render_template("index.html"), 422

    name = normalize_url(raw_url)
    if not is_valid_url(name):
        flash("Некорректный URL", "danger")
        return render_template("index.html"), 422

    if not check_url_not_exists(conn, name):
        existing_id = get_id_by_name(conn, name)
        flash("Страница уже существует", "info")
        return redirect(url_for("url_details", id=existing_id))

    new_id = insert_url(conn, name)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("url_details", id=new_id))


@app.get("/urls/<int:id>")
@use_db_connection
def url_details(conn, id):
    if not is_valid_id(conn, id):
        flash("Страница не найдена", "danger")
        return redirect(url_for("index"))

    url_data, checks = get_url_with_checks(conn, id)
    return render_template("url_details.html", url=url_data, checks=checks)


@app.post("/urls/<int:id>/checks")
@use_db_connection
def check_url(conn, id):
    if not is_valid_id(conn, id):
        flash("Страница не найдена", "danger")
        return redirect(url_for("index"))

    name = get_name_by_id(conn, id)
    try:
        status_code, h1, title, description = fetch_url_data(name)
    except FetchError as e:
        if str(e) == "timeout":
            flash("Ошибка: время ожидания запроса истекло", "danger")
        else:
            flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for("url_details", id=id))

    insert_check(conn, id, status_code, h1, title, description)
    flash("Страница успешно проверена", "success")
    return redirect(url_for("url_details", id=id))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
