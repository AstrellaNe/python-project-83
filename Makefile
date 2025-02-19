PORT ?= 10000
# поменял порт для Render

# Локальная разработка
dev:
	uv run flask --debug --app page_analyzer:app run

# Запуск приложения локально через Gunicorn
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer.app:app

# Запуск приложения на Render
render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

install:
	poetry install

# Сборка проекта
build:
	./build.sh

# Проверка кода
lint:
	poetry run flake8

# Запуск тестов
test:
	# Проверяем код с помощью flake8
	poetry run pytest
