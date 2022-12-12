import datetime
from pathlib import Path

from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import BaseSettings, EmailStr


class Database(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    def get_db_name(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_test_db(self):
        return f"postgresql+asyncpg://test:test@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/test"

    class Config:
        env_file = ".env"


class Settings(BaseSettings):
    DOCS_URL: str | None = None
    SMS_TOKEN: str
    EMAIL_LOGIN: EmailStr
    EMAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    SECRET: str
    HASH_ALGORITHM: str
    NOTIFICATION_HOUR: int = 14
    DEBUG: bool = False
    BASE_DIR: Path = None
    PAYMENTS_DIR: Path = None
    MEDIA_DIR: Path = None
    STATIC_DIR: Path = None
    TEMPLATES_DIR: Path = None
    LOGS_DIR: Path = None
    CREATE_FAKE_DATA: bool = False
    CREATE_ADMIN: bool = False
    DEFAULT_ADMIN: dict = {}
    RECREATE_DB: bool = False
    ECHO: bool = False
    STAGE: str = 'test'

    class Config:
        env_file = ".env"


class Prodamus(BaseSettings):
    PRODAMUS_SYS_KEY: str
    NOTIFICATION_URL: str
    SUCCESS_URL: str
    RETURN_URL: str


BASE_DIR = Path(__file__).parent

env_file = BASE_DIR / '.env'
db = Database(_env_file=env_file, _env_file_encoding='utf-8')
settings = Settings(_env_file=env_file, _env_file_encoding='utf-8')
prodamus = Prodamus(_env_file=env_file, _env_file_encoding='utf-8')

settings.BASE_DIR = BASE_DIR
settings.TEMPLATES_DIR = settings.TEMPLATES_DIR if settings.TEMPLATES_DIR else settings.BASE_DIR / 'templates'
settings.STATIC_DIR = settings.STATIC_DIR if settings.STATIC_DIR else settings.BASE_DIR / 'static'
settings.MEDIA_DIR = settings.MEDIA_DIR if settings.MEDIA_DIR else settings.BASE_DIR / 'media'
settings.PAYMENTS_DIR = settings.PAYMENTS_DIR if settings.PAYMENTS_DIR else settings.BASE_DIR / 'payments'

if not settings.STATIC_DIR.exists():
    logger.warning(f"Static directory {settings.STATIC_DIR} does not exists")
    exit()


if not settings.MEDIA_DIR.exists():
    logger.warning(f"Media directory {settings.MEDIA_DIR} does not exists")
    Path.mkdir(settings.MEDIA_DIR, exist_ok=True, parents=True)
    exit()

if not settings.LOGS_DIR:
    current_date = str(datetime.datetime.today().date())
    settings.LOGS_DIR = BASE_DIR / 'logs' / current_date

LEVEL_UP_PERCENTS = 70
MAX_VIDEO = 10
MAX_LEVEL = 10
log_level = 1 if settings.DEBUG else 20
logger.add(level=log_level, sink=settings.LOGS_DIR / 'ci_api.log')

templates = Jinja2Templates(directory=settings.TEMPLATES_DIR, auto_reload=True)

PHONE_FORMAT = '9317776655'
