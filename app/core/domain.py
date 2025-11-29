from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

from .exceptions import InvalidPhaseConfiguration


class Direction(str, Enum):
    """
    Направления движения на перекрёстке.

    Для упрощения — две оси:
    - NS (North–South)
    - EW (East–West)
    """
    NS = "NS"
    EW = "EW"


class SignalColor(str, Enum):
    """
    Состояние сигнала светофора.
    """

    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


@dataclass(frozen=True)
class Phase:
    """
    Описание одной фазы цикла светофора.
    """

    name: str
    duration: int  # seconds
    states: Dict[Direction, SignalColor]


class TrafficController:
    """
    Управляет фазами светофора на одном перекрёстке.

    Основные обязанности:
    - хранит набор фаз;
    - обеспечивает переход между фазами;
    - проверяет, что конфигурация безопасна (нет конфликтующих зелёных);
    - предоставляет "снимок" текущего состояния.
    """

    def __init__(self, intersection_id: str, name: str, phases: List[Phase]):
        if not phases:
            raise ValueError("At least one phase is required")

        self.id = intersection_id
        self.name = name
        self.phases = phases
        self.current_index = 0
        self.elapsed_in_phase = 0

        self._validate_phases()

    def _validate_phases(self) -> None:
        """
        Простейшее правило безопасности:
        NS и EW не могут одновременно быть GREEN в одной фазе.

        Здесь можно было бы добавить более сложную матрицу конфликтов,
        но для учебного проекта достаточно такого правила.
        """
        if not self.phases:
            raise InvalidPhaseConfiguration("No phases configured")

        for phase in self.phases:
            if phase.duration <= 0:
                raise InvalidPhaseConfiguration(
                    f"Phase {phase.name} must have positive duration",
                )

            ns = phase.states.get(Direction.NS)
            ew = phase.states.get(Direction.EW)

            if ns is None or ew is None:
                raise InvalidPhaseConfiguration(
                    f"Phase {phase.name} must define NS and EW states",
                )

            if ns == SignalColor.GREEN and ew == SignalColor.GREEN:
                raise InvalidPhaseConfiguration(
                    f"Conflicting GREEN signals in phase {phase.name}",
                )

    @property
    def current_phase(self) -> Phase:
        return self.phases[self.current_index]

    def _next_phase(self) -> None:
        """
        Перейти к следующей фазе цикла по кругу.
        """
        self.current_index = (self.current_index + 1) % len(self.phases)
        self.elapsed_in_phase = 0

    def tick(self, seconds: int) -> None:
        """
        Продвинуть симуляцию на указанное число секунд.

        Может произойти несколько переходов между фазами.
        """
        if seconds < 0:
            raise ValueError("seconds must be non-negative")

        remaining = seconds
        while remaining > 0:
            phase = self.current_phase
            time_left = phase.duration - self.elapsed_in_phase

            if remaining < time_left:
                self.elapsed_in_phase += remaining
                remaining = 0
            else:
                remaining -= time_left
                self._next_phase()

    def reset(self) -> None:
        """
        Сбросить симуляцию: вернуться в первую фазу, время в фазе = 0.
        """
        self.current_index = 0
        self.elapsed_in_phase = 0

    def state_snapshot(self) -> dict:
        """
        Получить "снимок" текущего состояния перекрёстка.
        Используется для сериализации в REST API.
        """
        phase = self.current_phase
        return {
            "intersection_id": self.id,
            "intersection_name": self.name,
            "phase_name": phase.name,
            "elapsed_in_phase": self.elapsed_in_phase,
            "phase_duration": phase.duration,
            "signals": {
                direction.value: color.value
                for direction, color in phase.states.items()
            },
        }
