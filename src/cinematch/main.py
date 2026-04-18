"""ASGI entrypoint for the CineMatch AI web application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from cinematch.api.movielens_routes import router as movielens_router
from cinematch.api.routes import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="CineMatch AI",
        description="Movie recommendations API and UI (scaffold).",
        version="0.1.0",
    )

    static_dir = Path(__file__).resolve().parent / "static"

    @app.get("/")
    def root() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    app.include_router(api_router, prefix="/api")
    app.include_router(movielens_router, prefix="/api/movielens")
    app.mount(
        "/static",
        StaticFiles(directory=static_dir),
        name="static",
    )
    return app


app = create_app()
