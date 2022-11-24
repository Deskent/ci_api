import datetime
from pathlib import Path

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


class Settings(BaseSettings):
    EMAIL_LOGIN: EmailStr
    EMAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    SECRET: str
    DEBUG: bool = False
    BASE_DIR: str | Path = None
    MEDIA_DIR: str | Path = None
    STATIC_DIR: str | Path = None
    LOGS_DIR: str | Path = None
    CREATE_FAKE_DATA: bool = False
    CREATE_ADMIN: bool = False
    DEFAULT_ADMIN: dict = {}


BASE_DIR = Path(__file__).parent


env_file = BASE_DIR / '.env'
db = Database(_env_file=env_file, _env_file_encoding='utf-8')
settings = Settings(_env_file=env_file, _env_file_encoding='utf-8')

if not settings.BASE_DIR:
    settings.BASE_DIR = BASE_DIR
if not settings.STATIC_DIR:
    settings.STATIC_DIR = settings.BASE_DIR / 'static'
if not settings.MEDIA_DIR:
    settings.MEDIA_DIR = settings.STATIC_DIR / 'media'
if not settings.LOGS_DIR:
    current_date = str(datetime.datetime.today().date())
    settings.LOGS_DIR = BASE_DIR / 'logs' / current_date

LEVEL_UP = 70
MAX_VIDEO = 10
log_level = 1 if settings.DEBUG else 20
logger.add(level=log_level, sink=settings.LOGS_DIR / 'ci_api.log')
