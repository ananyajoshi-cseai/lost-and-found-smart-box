import logging
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .auth import validate_configuration
from .database import initialize
from .routers import events, search, items, claims, admin


@asynccontextmanager
async def lifespan(app):
    validate_configuration()
    initialize()
    yield


app = FastAPI(title="Smart Box", version="0.1.0", lifespan=lifespan)
app.include_router(events.router)
app.include_router(search.router)
app.include_router(items.router)
app.include_router(claims.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Keep operational details in server logs, never in public error bodies.
@app.exception_handler(sqlite3.Error)
async def database_error(request, error):
    logging.getLogger(__name__).error("Database operation failed", exc_info=error)
    return JSONResponse(status_code=500, content={"detail": "Database operation failed"})

@app.exception_handler(OSError)
async def storage_error(request, error):
    logging.getLogger(__name__).error("Storage operation failed", exc_info=error)
    return JSONResponse(status_code=500, content={"detail": "Storage operation failed"})
