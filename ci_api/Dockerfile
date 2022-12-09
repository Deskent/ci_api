FROM python:3.10-alpine as builder

RUN apk update && apk upgrade && apk add ffmpeg

RUN python3 -m pip install --no-cache-dir --upgrade pip

FROM builder

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . .
