#!/usr/bin/env bash

# Устанавливаем uv, если он не установлен
if ! command -v uv &> /dev/null; then
    echo "🔧 Устанавливаем uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
fi

# Устанавливаем зависимости через Makefile
make install

# Применяем миграции к базе данных
psql -a -d $DATABASE_URL -f database.sql
