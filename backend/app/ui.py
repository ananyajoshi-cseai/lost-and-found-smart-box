"""Serve the team's frontend from the API origin, without exposing backend files."""
import os
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
DEV_ORIGINS = {"http://localhost:5500", "http://127.0.0.1:5500"}


def configure_ui(app, frontend=FRONTEND):
    frontend = Path(frontend).resolve()
    origins = [value.strip() for value in os.getenv("CORS_ORIGINS", "").split(",") if value.strip()]
    if not set(origins) <= DEV_ORIGINS:
        raise ValueError("CORS_ORIGINS may contain only the documented localhost:5500 and 127.0.0.1:5500 origins")
    if origins:
        app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                           allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])

    @app.get("/ui", include_in_schema=False)
    def ui_redirect():
        return RedirectResponse("/ui/")

    @app.get("/ui/", include_in_schema=False)
    def ui_index():
        index = frontend / "index.html"
        if not index.is_file() or index.resolve().parent != frontend:
            return JSONResponse(status_code=503, content={"detail": "Frontend is not available yet. Add the reviewed frontend/index.html; use /docs to exercise the backend meanwhile."})
        return FileResponse(index, headers={"Cache-Control": "no-store"})

    # Mount only frontend/, never the repository, database or uploads directory.
    app.mount("/ui", StaticFiles(directory=frontend, html=True, check_dir=False), name="ui")
