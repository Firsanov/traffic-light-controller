from typing import Dict, List

from pydantic import BaseModel, Field, validator

from .domain import Direction, SignalColor


class ErrorResponse(BaseModel):
    """
    Стандартный формат ошибки для API.
    """

    detail: str


class IntersectionSummary(BaseModel):
    id: str
    name: str


class IntersectionState(BaseModel):
    intersection_id: str
    intersection_name: str
    phase_name: str
    elapsed_in_phase: int
    phase_duration: int
    signals: Dict[str, str]


class PhaseConfig(BaseModel):
    """
    Конфигурация фазы, получаемая/отдаваемая через API.
    """

    name: str = Field(..., example="NS_GREEN")
    duration: int = Field(..., gt=0, example=30)
    states: Dict[Direction, SignalColor]

    @validator("states")
    def validate_states(cls, v: Dict[Direction, SignalColor]) -> Dict[Direction, SignalColor]:
        # Проверяем, что NS и EW присутствуют
        if Direction.NS not in v or Direction.EW not in v:
            raise ValueError("states must contain NS and EW directions")
        return v


class IntersectionConfig(BaseModel):
    """
    Полная конфигурация перекрёстка, включая фазы.
    """

    id: str = Field(..., example="main-crossroad")
    name: str = Field(..., example="Main intersection")
    phases: List[PhaseConfig]


class IntersectionCreateRequest(BaseModel):
    """
    Тело запроса для создания нового перекрёстка.
    """

    name: str
    phases: List[PhaseConfig]


class IntersectionConfigResponse(BaseModel):
    """
    Ответ с конфигурацией перекрёстка.
    """

    id: str
    name: str
    phases: List[PhaseConfig]


class IntersectionsListResponse(BaseModel):
    items: List[IntersectionSummary]


class TickRequest(BaseModel):
    seconds: int = Field(
        ...,
        gt=0,
        description="How many seconds to advance in the simulation",
    )
