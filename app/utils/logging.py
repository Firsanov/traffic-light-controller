import logging
from typing import Optional

from ..config import Settings


def configure_logging(settings: Settings) -> None:
    """
    Базовая настройка логирования.

    В реальном проекте сюда можно добавить:
    - JSON-формат логов
    - интеграцию с Sentry / ELK и т.п.
    """
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or "traffic-light")
