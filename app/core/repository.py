from typing import Dict, List

from .domain import Direction, Phase, SignalColor, TrafficController
from .exceptions import IntersectionNotFound
from .models import IntersectionConfig, PhaseConfig


class InMemoryIntersectionRepository:
    """
    Простое in-memory хранилище.

    Можно заменить на работу с БД, не меняя интерфейс.
    """

    def __init__(self) -> None:
        self._items: Dict[str, TrafficController] = {}

    def add(self, controller: TrafficController) -> None:
        self._items[controller.id] = controller

    def get(self, intersection_id: str) -> TrafficController:
        try:
            return self._items[intersection_id]
        except KeyError as exc:
            raise IntersectionNotFound(
                f"Intersection {intersection_id} not found",
            ) from exc

    def list(self) -> List[TrafficController]:
        return list(self._items.values())

    def delete(self, intersection_id: str) -> None:
        if intersection_id not in self._items:
            raise IntersectionNotFound(
                f"Intersection {intersection_id} not found",
            )
        del self._items[intersection_id]

    def clear(self) -> None:
        self._items.clear()


repo = InMemoryIntersectionRepository()


def _phases_from_config(phases_config: List[PhaseConfig]) -> List[Phase]:
    phases: List[Phase] = []
    for ph in phases_config:
        phases.append(
            Phase(
                name=ph.name,
                duration=ph.duration,
                states=ph.states,
            ),
        )
    return phases


def create_default_intersection() -> None:
    """
    Создаёт один дефолтный перекрёсток, если репозиторий пуст.

    Цикл:
    - NS_GREEN (30 c)
    - NS_YELLOW (5 c)
    - EW_GREEN (30 c)
    - EW_YELLOW (5 c)
    """
    if repo.list():
        return

    phases_config = [
        PhaseConfig(
            name="NS_GREEN",
            duration=30,
            states={
                Direction.NS: SignalColor.GREEN,
                Direction.EW: SignalColor.RED,
            },
        ),
        PhaseConfig(
            name="NS_YELLOW",
            duration=5,
            states={
                Direction.NS: SignalColor.YELLOW,
                Direction.EW: SignalColor.RED,
            },
        ),
        PhaseConfig(
            name="EW_GREEN",
            duration=30,
            states={
                Direction.NS: SignalColor.RED,
                Direction.EW: SignalColor.GREEN,
            },
        ),
        PhaseConfig(
            name="EW_YELLOW",
            duration=5,
            states={
                Direction.NS: SignalColor.RED,
                Direction.EW: SignalColor.YELLOW,
            },
        ),
    ]

    phases = _phases_from_config(phases_config)
    controller = TrafficController(
        intersection_id="default",
        name="Main intersection",
        phases=phases,
    )
    repo.add(controller)


def save_from_config(config: IntersectionConfig) -> TrafficController:
    """
    Создаёт или перезаписывает перекрёсток из полной конфигурации.
    """
    phases = _phases_from_config(config.phases)
    controller = TrafficController(
        intersection_id=config.id,
        name=config.name,
        phases=phases,
    )
    repo.add(controller)
    return controller
