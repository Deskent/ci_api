python 3.10


Приложение запускается в докере (необходимо установить докер и докер-компос)

Сначала копируем все из файла .env-template в файл .env и заполняем нужные поля.

Запускаем

    docker-compose up --build -d


ВАЖНО! 

Для доступ к медиа файлам ИЗ ПРИЛОЖЕНИЙ ФРОНТЕНДА нужно передавать дополнительный заголово Media со значением 

    dNf1br7bGa9b9VAlvgjOIId!177y=3JEo0jbkbBsuwTvIWp=zM-Jzc1X7QuXSXJcgNYL/ag6I-SvJJIqVp7oHjJ

Пример:

    curl -X 'GET' \               
    'https://energy.qidoctor.ru/media/hello.mp4' \
    -H 'accept: application/json' \
    -H 'Media: dNf1br7bGa9b9VAlvgjOIId!177y=3JEo0jbkbBsuwTvIWp=zM-Jzc1X7QuXSXJcgNYL/ag6I-SvJJIqVp7oHjJ'
