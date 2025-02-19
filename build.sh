#!/usr/bin/env bash

# Устанавливаем uv и зависимости
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Устанавливаем зависимости проекта
make install

# Загружаем SQL-схему в базу
psql -a -d $DATABASE_URL -f database.sql
