from fastapi import APIRouter, Depends, HTTPException, Path, status

from ...config import Settings
from ...core.exceptions import DomainError, IntersectionNotFound
from ...core.models import (
    ErrorResponse,
    IntersectionConfig,
    IntersectionConfigResponse,
    IntersectionState,
    IntersectionsListResponse,
    TickRequest,
)
from ...core.services import (
    create_or_update_intersection_service,
    delete_intersection_service,
    get_intersection_state_service,
    list_intersections_service,
    reset_intersection_service,
    tick_intersection_service,
)
from ..deps import get_settings_dep
from ...utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/",
    response_model=IntersectionsListResponse,
    summary="List intersections",
    tags=["intersections"],
)
def list_intersections(
    settings: Settings = Depends(get_settings_dep),
) -> IntersectionsListResponse:
    """
    Возвращает список всех перекрёстков.
    """
    items = list_intersections_service()
    logger.debug("Listing intersections (%d items)", len(items))
    return IntersectionsListResponse(items=items)


@router.get(
    "/{intersection_id}/state",
    response_model=IntersectionState,
    responses={404: {"model": ErrorResponse}},
    summary="Get current traffic light state",
    tags=["intersections"],
)
def get_state(
    intersection_id: str = Path(..., description="Intersection identifier"),
    settings: Settings = Depends(get_settings_dep),
) -> IntersectionState:
    """
    Получить текущее состояние светофора на перекрёстке.
    """
    try:
        snapshot = get_intersection_state_service(intersection_id)
    except IntersectionNotFound as exc:
        logger.warning("Intersection not found: %s", intersection_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return IntersectionState(**snapshot)


@router.post(
    "/{intersection_id}/tick",
    response_model=IntersectionState,
    responses={404: {"model": ErrorResponse}},
    summary="Advance simulation time",
    tags=["intersections"],
)
def tick(
    intersection_id: str = Path(..., description="Intersection identifier"),
    body: TickRequest | None = None,
    settings: Settings = Depends(get_settings_dep),
) -> IntersectionState:
    """
    Продвинуть симуляцию на указанное количество секунд.
    """
    if body is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is required",
        )

    try:
        snapshot = tick_intersection_service(intersection_id, body.seconds)
    except IntersectionNotFound as exc:
        logger.warning("Intersection not found on tick: %s", intersection_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DomainError as exc:
        logger.error("Domain error on tick: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return IntersectionState(**snapshot)


@router.post(
    "/{intersection_id}/reset",
    response_model=IntersectionState,
    responses={404: {"model": ErrorResponse}},
    summary="Reset simulation for intersection",
    tags=["intersections"],
)
def reset(
    intersection_id: str = Path(..., description="Intersection identifier"),
    settings: Settings = Depends(get_settings_dep),
) -> IntersectionState:
    """
    Сброс симуляции перекрёстка.
    """
    try:
        snapshot = reset_intersection_service(intersection_id)
    except IntersectionNotFound as exc:
        logger.warning("Intersection not found on reset: %s", intersection_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return IntersectionState(**snapshot)


@router.put(
    "/{intersection_id}",
    response_model=IntersectionConfigResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Create or update intersection configuration",
    tags=["intersections"],
)
def create_or_update_intersection(
    intersection_id: str = Path(..., description="Intersection identifier"),
    body: IntersectionConfig | None = None,
    settings: Settings = Depends(get_settings_dep),
) -> IntersectionConfigResponse:
    """
    Создать новый или обновить существующий перекрёсток.

    Идентификатор в path и в body должен совпадать.
    """
    if body is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is required",
        )

    if body.id != intersection_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Intersection id in path and body must match",
        )

    try:
        result = create_or_update_intersection_service(body)
    except DomainError as exc:
        logger.error("Domain error on create_or_update: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return result


@router.delete(
    "/{intersection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Delete intersection",
    tags=["intersections"],
)
def delete_intersection(
    intersection_id: str = Path(..., description="Intersection identifier"),
    settings: Settings = Depends(get_settings_dep),
) -> None:
    """
    Удалить перекрёсток.
    """
    try:
        delete_intersection_service(intersection_id)
    except IntersectionNotFound as exc:
        logger.warning("Intersection not found on delete: %s", intersection_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
