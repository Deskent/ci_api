VERSION="manual" APPNAME="ci_api" docker-compose build &&
VERSION="manual" APPNAME="ci_api" docker-compose run --rm app pytest -k server tests/ &&
VERSION="manual" APPNAME="ci_api" docker-compose down --remove-orphans &&
VERSION="manual" APPNAME="ci_api" docker-compose up --build -d &&
docker logs ci_api-manual -f
