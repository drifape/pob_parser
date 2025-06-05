FROM python:3.12

# 1. Базовые системные пакеты + LuaJIT + LuaRocks
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    luajit \
    luarocks \
 && rm -rf /var/lib/apt/lists/*

# 2. Устанавливаем модуль UTF-8: luautf8 0.1.4-1 (под LuaJIT/Lua 5.1)
RUN luarocks install luautf8 0.1.4-1

# 3. Клонируем Path of Building Community Fork (ветка dev)
RUN git clone --branch dev https://github.com/PathOfBuildingCommunity/PathOfBuilding.git /pob

# 4. Переменные окружения для Lua
ENV LUA_PATH="/pob/runtime/lua/?.lua;/pob/runtime/lua/?/init.lua;;"
ENV PYTHONUNBUFFERED=1

# 5. Приложение FastAPI
WORKDIR /app
COPY ./app /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Запуск сервера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
