from pydantic import BaseSettings
from dotenv import load_dotenv
import os

class CommonSettings(BaseSettings):
    APP_NAME: str = "GD4H CENSUS APP"
    DEBUG_MODE: bool = False


class ServerSettings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000


class DatabaseSettings(BaseSettings):
    DB_URL: str
    DB_NAME: str


class Settings(CommonSettings, ServerSettings, DatabaseSettings):
    env_file = "~/projects/GD4H/FARM-Intro/backend/.env"
    load_dotenv()
    APP_NAME = os.getenv("APP_NAME")
    DB_NAME = os.getenv("DB_NAME")
    DB_URL = os.getenv("DB_URL")
    DEBUG_MODE = bool(os.getenv("DEBUG_MODE"))
    


settings = Settings()
