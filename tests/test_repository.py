import pytest

from app.core.domain import Direction, Phase, SignalColor, TrafficController
from app.core.exceptions import IntersectionNotFound
from app.core.repository import InMemoryIntersectionRepository


def create_controller(id_: str = "id") -> TrafficController:
    phases = [
        Phase(
            name="P1",
            duration=5,
            states={Direction.NS: SignalColor.GREEN, Direction.EW: SignalColor.RED},
        ),
        Phase(
            name="P2",
            duration=5,
            states={Direction.NS: SignalColor.RED, Direction.EW: SignalColor.GREEN},
        ),
    ]
    return TrafficController(id_, "name", phases)


def test_add_and_get() -> None:
    repo = InMemoryIntersectionRepository()
    controller = create_controller("abc")
    repo.add(controller)

    fetched = repo.get("abc")
    assert fetched.id == "abc"


def test_get_not_found_raises() -> None:
    repo = InMemoryIntersectionRepository()
    with pytest.raises(IntersectionNotFound):
        repo.get("missing")


def test_delete() -> None:
    repo = InMemoryIntersectionRepository()
    controller = create_controller("abc")
    repo.add(controller)

    repo.delete("abc")
    with pytest.raises(IntersectionNotFound):
        repo.get("abc")
