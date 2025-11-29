from typing import List

from .domain import TrafficController
from .models import (
    IntersectionConfig,
    IntersectionConfigResponse,
    IntersectionSummary,
)
from .repository import repo, save_from_config


def list_intersections_service() -> List[IntersectionSummary]:
    controllers: List[TrafficController] = repo.list()
    return [
        IntersectionSummary(
            id=c.id,
            name=c.name,
        )
        for c in controllers
    ]


def get_intersection_state_service(intersection_id: str) -> dict:
    controller = repo.get(intersection_id)
    return controller.state_snapshot()


def tick_intersection_service(intersection_id: str, seconds: int) -> dict:
    controller = repo.get(intersection_id)
    controller.tick(seconds)
    return controller.state_snapshot()


def reset_intersection_service(intersection_id: str) -> dict:
    controller = repo.get(intersection_id)
    controller.reset()
    return controller.state_snapshot()


def delete_intersection_service(intersection_id: str) -> None:
    repo.delete(intersection_id)


def create_or_update_intersection_service(
    config: IntersectionConfig,
) -> IntersectionConfigResponse:
    controller = save_from_config(config)
    phases = []
    for phase in controller.phases:
        phases.append(
            {
                "name": phase.name,
                "duration": phase.duration,
                "states": phase.states,
            },
        )

    return IntersectionConfigResponse(
        id=controller.id,
        name=controller.name,
        phases=phases,
    )
