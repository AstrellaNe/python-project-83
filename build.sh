#!/usr/bin/env bash

echo "🚀 Запуск сборки проекта..."

# Устанавливаем зависимости через Poetry (вместо uv)
echo " Устанавливаем зависимости..."
poetry install

# Проверка на наличие переменной DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Переменная DATABASE_URL не задана!"
    exit 1
fi

# Применяем миграции к базе данных
echo "🔄 Применяем миграции к базе данных..."
psql "$DATABASE_URL" -f database.sql

echo "✅ Сборка завершена успешно!"
