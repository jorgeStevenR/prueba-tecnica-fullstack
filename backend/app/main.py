from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.config import get_settings
from app.infrastructure.db import get_database
from app.infrastructure.repositories import TinyDBUserRepository
from app.infrastructure.seed import seed_default_user
from app.web.exception_handlers import register_exception_handlers
from app.web.routers import auth, numbers


@asynccontextmanager
async def lifespan(_: FastAPI):
    db = get_database()
    seed_default_user(TinyDBUserRepository(db))
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Prueba Tecnica Fullstack API",
        version="1.0.0",
        description="API REST con JWT, refresh token y CRUD de numeros.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(auth.router)
    app.include_router(numbers.router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
