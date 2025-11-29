from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Глобальные настройки приложения.

    Читаются из переменных окружения или .env файла.
    """

    app_name: str = "Traffic Light Control Service"
    app_env: str = "development"  # development / production
    log_level: str = "INFO"  # DEBUG / INFO / WARNING / ERROR
    api_v1_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Кешированная загрузка настроек — чтобы не создавать объект
    Settings каждый раз.
    """
    return Settings()
