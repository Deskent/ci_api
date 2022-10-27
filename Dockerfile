FROM python:3.10-slim as builder

RUN apt-get update && \
    apt-get install -y libpq-dev gcc

RUN python3 -m pip install --no-cache-dir --upgrade pip

FROM builder

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .
