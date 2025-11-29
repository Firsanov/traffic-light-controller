from fastapi import FastAPI

from .api.routes.intersections import router as intersections_router
from .config import get_settings
from .core.repository import create_default_intersection
from .utils.logging import configure_logging, get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description=(
            "Headless REST-сервис для моделирования работы системы "
            "управления светофорами на городских перекрёстках."
        ),
    )

    @app.on_event("startup")
    def on_startup() -> None:  # type: ignore[unused-ignore]
        logger.info("Application starting up in %s mode", settings.app_env)
        create_default_intersection()
        logger.info("Default intersection initialized")

    @app.on_event("shutdown")
    def on_shutdown() -> None:  # type: ignore[unused-ignore]
        logger.info("Application shutting down")

    @app.get("/health", tags=["health"])
    def health() -> dict:  # type: ignore[unused-ignore]
        """
        Простой health-check для оркестратора/балансировщика.
        """
        return {"status": "ok"}

    app.include_router(
        intersections_router,
        prefix=f"{settings.api_v1_prefix}/intersections",
    )

    return app


app = create_app()
