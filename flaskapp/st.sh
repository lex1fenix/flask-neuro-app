#!/bin/bash
gunicorn --bind 127.0.0.1:5000 wsgi:app &
APP_PID=$!
sleep 5

echo "PID сервера: $APP_PID"

# можно добавить тестовый запрос
# python3 client.py

kill -TERM $APP_PID
echo "Сервер остановлен"
exit 0
