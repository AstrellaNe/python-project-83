PORT ?= 8000

dev:
	# Запускаем приложение Flask локально
	poetry run flask --app page_analyzer run --port $(PORT)

start:
	# Запускаем Gunicorn с 5 рабочими процессами
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) app:app

start-full:
	# Устанавливаем зависимости и собираем проект перед запуском
	make install
	make build
	flask --app page_analyzer --debug run --port $(PORT)

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

git-prepare:
	# Собираем проект и добавляем в Git
	make build
	git add .

build:
	# Делаем скрипт `build.sh` исполняемым и запускаем его
	chmod +x build.sh
	./build.sh
