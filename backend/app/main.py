from collections.abc import Iterable

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import health, root, tasks, training, ws
from app.core.errors import AppError


def create_app(extra_routers: Iterable[APIRouter] | None = None) -> FastAPI:
    application = FastAPI(title="Embodied AI Training Platform")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    application.include_router(root.router)
    application.include_router(health.router)
    application.include_router(tasks.router)
    application.include_router(training.router)
    application.include_router(ws.router)
    for router in extra_routers or []:
        application.include_router(router)
    return application


app = create_app()
