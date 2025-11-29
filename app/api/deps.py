from ..config import Settings, get_settings
from ..core.repository import repo
from ..utils.logging import get_logger

logger = get_logger(__name__)


def get_settings_dep() -> Settings:
    return get_settings()


def get_repository_dep():
    """
    В реальном приложении тут можно было бы возвращать репозиторий,
    завязанный на БД.
    """
    return repo
