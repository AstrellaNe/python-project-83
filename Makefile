PORT ?= 8000

dev:
	# Запускаем приложение Flask локально
	FLASK_APP=page_analyzer poetry run flask run --port $(PORT)

start:
	# Запускаем Gunicorn с 5 рабочими процессами
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) app:app

start-full:
	# Устанавливаем зависимости и собираем проект перед запуском
	make install
	make build
	FLASK_APP=page_analyzer poetry run flask run --port $(PORT) --debug

start-gunicorn:
	# Запускаем приложение с Gunicorn (Production Mode)
	poetry run gunicorn --workers=4 --bind=0.0.0.0:$(PORT) app:app

install:
	# Устанавливаем зависимости проекта
	poetry install

poetry-build:
	# Собираем проект с помощью Poetry
	poetry build

lint:	
	# Проверяем код с помощью flake8
	poetry run flake8

test:
	# Запускаем тесты с pytest
	poetry run pytest

git-prepare:
	# Собираем проект и добавляем в Git
	make build
	git add .

build:
	# Запускаем сборку проекта
	./build.sh
