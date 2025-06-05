FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y git build-essential luajit curl && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/PathOfBuildingCommunity/PathOfBuilding.git /pob

WORKDIR /app
COPY ./app /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV LUA_PATH="/pob/runtime/lua/?.lua;/pob/runtime/lua/?/init.lua;;"
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
