FROM python:3.10-alpine

RUN python3 -m pip install --no-cache-dir --upgrade pip

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY .. .
