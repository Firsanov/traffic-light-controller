class DomainError(Exception):
    """
    Базовый класс для всех доменных ошибок.
    """


class IntersectionNotFound(DomainError):
    """
    Перекрёсток с указанным id не найден.
    """


class InvalidPhaseConfiguration(DomainError):
    """
    Ошибка в конфигурации фаз светофора (конфликтующие сигналы и т.п.).
    """
