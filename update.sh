#!/bin/bash

# Путь к проекту (можно оставить пустым, если запускаешь из корня)
PROJECT_DIR=$(pwd)

# Переход в папку проекта (опционально)
cd "$PROJECT_DIR" || { echo "Не могу перейти в папку проекта"; exit 1; }

# Останавливаем и удаляем старые контейнеры
echo "Останавливаем текущие контейнеры..."
docker-compose down

# Обновляем код из репозитория (если используется git)
# echo "Обновляем код из репозитория..."
# git pull origin main

# Пересобираем образы
echo "Пересобираем Docker-образы..."
docker-compose build --no-cache

# Запускаем контейнеры в фоне
echo "Запускаем контейнеры..."
docker-compose up -d

# Выводим статус контейнеров
echo ""
echo "Статус контейнеров:"
docker-compose ps

# Показываем последние логи
echo ""
echo "Последние логи reporter:"
docker-compose logs reporter | tail -n 20