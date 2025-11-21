from smtplib import SMTP
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    PROJECT_NAME: str = ""
    PROJECT_DESCRIPTION: str = ""
    API_V1_STR: str = ""
    SITE_NAME: str = ""
    LOG_DIR: str = ""
    DATABASE_URL: str = ""
    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = ""
    SMTP_HOST: str = "mailpit"
    SMTP_PORT: int = 1025
    MAILPIT_UI_PORT: int = 8025

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    
    # class Config:
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"
    #     extra = "ignore"


settings = Settings()