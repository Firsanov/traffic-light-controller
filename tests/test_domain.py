import pytest

from app.core.domain import Direction, Phase, SignalColor, TrafficController
from app.core.exceptions import InvalidPhaseConfiguration


def test_valid_phases_do_not_raise() -> None:
    phases = [
        Phase(
            name="P1",
            duration=10,
            states={Direction.NS: SignalColor.GREEN, Direction.EW: SignalColor.RED},
        ),
        Phase(
            name="P2",
            duration=10,
            states={Direction.NS: SignalColor.RED, Direction.EW: SignalColor.GREEN},
        ),
    ]

    controller = TrafficController("id", "name", phases)
    assert len(controller.phases) == 2
    assert controller.current_phase.name == "P1"


def test_conflicting_green_raises_error() -> None:
    phases = [
        Phase(
            name="BAD",
            duration=10,
            states={
                Direction.NS: SignalColor.GREEN,
                Direction.EW: SignalColor.GREEN,
            },
        ),
    ]

    with pytest.raises(InvalidPhaseConfiguration):
        TrafficController("id", "name", phases)


def test_tick_moves_to_next_phase() -> None:
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
    controller = TrafficController("id", "name", phases)

    assert controller.current_phase.name == "P1"
    controller.tick(5)
    assert controller.current_phase.name == "P2"


def test_multiple_phase_transitions() -> None:
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
    controller = TrafficController("id", "name", phases)

    controller.tick(12)
    assert controller.current_phase.name == "P1"
    assert controller.elapsed_in_phase == 2
