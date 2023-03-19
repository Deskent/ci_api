Develop state:
<img src="https://github.com/Deskent/ci_api/workflows/ci_api_tests/badge.svg?branch=develop"><br>

python 3.10

project in progress


ВАЖНО! 

Для доступ к медиа файлам нужно передавать дополнительный заголово Media со значением 

    dNf1br7bGa9b9VAlvgjOIId!177y=3JEo0jbkbBsuwTvIWp=zM-Jzc1X7QuXSXJcgNYL/ag6I-SvJJIqVp7oHjJ

Пример:

    curl -X 'GET' \               
    'https://energy.qidoctor.ru/media/hello.mp4' \
    -H 'accept: application/json' \
    -H 'Media: dNf1br7bGa9b9VAlvgjOIId!177y=3JEo0jbkbBsuwTvIWp=zM-Jzc1X7QuXSXJcgNYL/ag6I-SvJJIqVp7oHjJ'
