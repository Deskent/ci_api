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

Вся должна статика храниться в

    /var/www/ci_api

Если она будет в другом месте - нужно прописать в конфиге nginx и в файле
docker-compose.yml

# Nginx

Конфиг находится в папке nginx

    FOLDER_NAME/nginx/ci_api.conf

# Start

Переходим в папку

    cd FOLDER_NAME

Запускаем контейнеры

    . ./restart.sh
