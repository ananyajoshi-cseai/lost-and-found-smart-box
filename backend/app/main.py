from contextlib import asynccontextmanager
from fastapi import FastAPI
from .auth import validate_configuration
from .database import initialize
from .routers import events, search


@asynccontextmanager
async def lifespan(app):
    validate_configuration()
    initialize()
    yield


app = FastAPI(title="Smart Box", version="0.1.0", lifespan=lifespan)
app.include_router(events.router)
app.include_router(search.router)


@app.get("/health")
def health():
    return {"status": "ok"}
