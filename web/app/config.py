from pydantic import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    DB_URL: str
    TESTS_DB_URL: str

settings = Settings()
