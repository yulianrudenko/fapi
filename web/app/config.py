import os

from pydantic import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    SECRET_KEY: str
    DB_URL: str
    TESTS_DB_URL: str
    HOSTNAME: str
    BASE_DIR = Path(__file__).resolve().parent.parent
    MEDIA_DIR: str = os.path.join(BASE_DIR, 'media')
    STATIC_DIR: str = os.path.join(BASE_DIR, 'static')
    USER_IMAGES_FOLDER: str = 'images'

settings = Settings()
