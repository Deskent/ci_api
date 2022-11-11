from pathlib import Path
from pydantic import BaseSettings, EmailStr


class Database(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    RECREATE_DB: bool = False

    def get_db_name(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class Settings(BaseSettings):
    EMAIL_LOGIN: EmailStr
    EMAIL_PASSWORD: str
    SECRET: str
    DEBUG: bool = False
    BASE_DIR: str = ''
    MEDIA_DIR: str = ''
    TEMPLATES_DIR: str = ''


BASE_DIR = Path(__file__).parent
MEDIA_DIR = BASE_DIR / 'media'
TEMPLATES_DIR = BASE_DIR / 'templates'

env_file = BASE_DIR / '.env'
db = Database(_env_file=env_file, _env_file_encoding='utf-8')
settings = Settings(_env_file=env_file, _env_file_encoding='utf-8')

settings.BASE_DIR = BASE_DIR
settings.MEDIA_DIR = MEDIA_DIR
settings.TEMPLATES_DIR = TEMPLATES_DIR

LEVEL_UP = 70
