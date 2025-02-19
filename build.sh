#!/usr/bin/env bash

# Установка uv и установка зависимостей
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
make install
