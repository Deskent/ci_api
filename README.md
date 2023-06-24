# Stack

    Python 3.10

    Docker

    Postgres 14

    Redis

    FastAPI

# Deploy

Клонируем репозиторий

    git clone git@gitlab.cygenic.tech:cy_application/backend.git FOLDER_NAME

Копируем переменные окружения в файл 'FOLDER_NAME/ci_api/.env'
Описание необходимых переменных есть в файле FOLDER_NAME/ci_api/.env-template

# База данных

Чтобы загрузить начальные данные (настроения, приветственное видео и прочие)
в базу, нужен python3.10, с его помощью выполняем файл create_data.py

    cd FOLDER_NAME/ci_api

    python3.10 create_data.py


# Статика

Вся пользовательская статика (аватары, видео) должна храниться в

    /var/www/ci_api

При переносе просто скопируйте ее со старого на новый сервер в эту же папку.
Если она будет в другом месте - нужно прописать в конфиге nginx и в файле
docker-compose.yml.

# Nginx

Конфиг находится в папке nginx

    FOLDER_NAME/nginx/ci_api.conf

# Start

Переходим в папку

    cd FOLDER_NAME

Запускаем контейнеры

    . ./restart.sh

# Nota bene

1. Если будет запускаться больше одного воркера гуникорна (по умолчанию - один) - необходимо вынести планировщик
в отдельный сервис, чтобы он не дублировался в каждом воркере.

2. Для доступ к медиа файлам ИЗ ПРИЛОЖЕНИЙ ФРОНТЕНДА нужно передавать дополнительный заголовок Media со значением

    dNf1br7bGa9b9VAlvgjOIId!177y=3JEo0jbkbBsuwTvIWp=zM-Jzc1X7QuXSXJcgNYL/ag6I-SvJJIqVp7oHjJ

Пример:

    curl -X 'GET' \
    'https://energy.qidoctor.ru/media/hello.mp4' \
    -H 'accept: application/json' \
    -H 'Media: dNf1br7bGa9b9VAlvgjOIId!177y=3JEo0jbkbBsuwTvIWp=zM-Jzc1X7QuXSXJcgNYL/ag6I-SvJJIqVp7oHjJ'
