PORT ?= 8000

# Локальная разработка
dev:
	FLASK_APP=page_analyzer.app poetry run flask run --port $(PORT)

# Запуск приложения локально через Gunicorn
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer.app:app

# Запуск приложения на Render
render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

# Установка зависимостей
install:
	uv sync

# Сборка проекта
build:
	./build.sh

# Проверка кода
lint:
	poetry run flake8

# Запуск тестов
test:
	poetry run pytest
