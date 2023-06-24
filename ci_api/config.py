import datetime
import sys
from pathlib import Path

from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import BaseSettings, EmailStr, RedisDsn


class Database(BaseSettings):
    POSTGRES_DB: str = 'test'
    POSTGRES_HOST: str = '127.0.0.1'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = 'test'
    POSTGRES_PASSWORD: str = 'test'
    REDIS_DB: RedisDsn = 'redis://127.0.0.1:6379/0'

    def get_db_name(self):
        logger.warning(f'\n\nLoad DB: {self.POSTGRES_DB}\n\n')
        return (
            f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )

    class Config:
        env_file = '.env'


class Settings(BaseSettings):
    DOCS_URL: str = '/docs'
    ADMIN_URL: str = '/admin'
    SMS_TOKEN: str = 'some_token'
    EMAIL_LOGIN: EmailStr = 'test@mail.ru'
    EMAIL_PASSWORD: str = 'email_password'
    MAIL_PORT: int = 465
    MAIL_SERVER: str = 'smtp.mail.ru'
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    SECRET: str = 'some_secret'
    HASH_ALGORITHM: str = 'HS256'
    USE_CACHE: bool = False

    NOTIFICATION_HOUR: int = 14
    DEBUG: bool = False
    BASE_DIR: Path = None
    PAYMENTS_DIR: Path = None
    MEDIA_DIR: Path = None
    STATIC_DIR: Path = None
    TEMPLATES_DIR: Path = None
    LOGS_DIR: Path = None
    CREATE_FAKE_DATA: bool = False
    CREATE_ADMIN: bool = True
    DEFAULT_ADMIN: dict = {'username': 'test', 'email': 'test@mail.ru', 'password': 'test'}
    RECREATE_DB: bool = False
    ECHO: bool = False
    STAGE: str = 'prod'

    class Config:
        env_file = '.env'


class SiteMeta(BaseSettings):
    SITE_URL: str = 'http://127.0.0.1:8000'
    COMPANY_EMAIL: str = 'company@email.com'
    COMPANY_PHONE: str = '9992223344'
    VK_LINK: str = 'vk.com'
    YOUTUBE_LINK: str = 'youtube.com'
    GOOGLE_PLAY_LINK: str = 'https://www.google.com'
    APP_STORE_LINK: str = 'https://www.apple.com'


class Prodamus(BaseSettings):
    PRODAMUS_SYS_KEY: str = 'some_key'
    NOTIFICATION_URL: str = 'https://test.ru'
    SUCCESS_URL: str = 'https://test.ru'
    RETURN_URL: str = 'https://test.ru'
    PRODAMUS_MODE: str = 'test'


BASE_DIR = Path(__file__).parent

env_file = BASE_DIR / '.env'
db = Database(_env_file=env_file, _env_file_encoding='utf-8')
settings = Settings(_env_file=env_file, _env_file_encoding='utf-8')
prodamus = Prodamus(_env_file=env_file, _env_file_encoding='utf-8')
site = SiteMeta(_env_file=env_file, _env_file_encoding='utf-8')

settings.BASE_DIR = BASE_DIR
settings.TEMPLATES_DIR = settings.TEMPLATES_DIR \
    if settings.TEMPLATES_DIR else settings.BASE_DIR / 'templates'
settings.STATIC_DIR = settings.STATIC_DIR \
    if settings.STATIC_DIR else settings.BASE_DIR / 'static'
settings.MEDIA_DIR = settings.MEDIA_DIR \
    if settings.MEDIA_DIR else settings.BASE_DIR / 'media'
settings.PAYMENTS_DIR = settings.PAYMENTS_DIR \
    if settings.PAYMENTS_DIR else settings.BASE_DIR / 'payments'

if not settings.STATIC_DIR.exists():
    logger.warning(f'Static directory {settings.STATIC_DIR} does not exists')
    Path.mkdir(settings.STATIC_DIR, exist_ok=True, parents=True)

if not settings.MEDIA_DIR.exists():
    logger.warning(f'Media directory {settings.MEDIA_DIR} does not exists')
    Path.mkdir(settings.MEDIA_DIR, exist_ok=True, parents=True)

if not settings.LOGS_DIR:
    current_date = str(datetime.datetime.today().date())
    settings.LOGS_DIR = BASE_DIR / 'logs' / current_date

LEVEL_UP_PERCENTS = 70
MAX_VIDEO = 10
MAX_LEVEL = 10
log_level = 1 if settings.DEBUG else 20
logger.remove()
logger.add(level=log_level, sink=settings.LOGS_DIR / 'ci_api.log', rotation='50 MB')
logger.add(level=log_level, sink=sys.stdout)
logger.add(level=30, sink=settings.LOGS_DIR / 'errors.log', rotation='100 MB')

templates = Jinja2Templates(directory=settings.TEMPLATES_DIR, auto_reload=True)
