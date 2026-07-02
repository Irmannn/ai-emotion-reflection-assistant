from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers import reflections


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    yield


app = FastAPI(
    title="AI Emotion Reflection Assistant API",
    description="FastAPI backend for the AI emotion reflection assistant MVP.",
    version="0.1.0",
    lifespan=lifespan,
)

# Keep CORS narrow in early development. The frontend dev server runs on port 3000.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple response so local setup can verify the backend is alive."""
    return {"status": "ok"}


app.include_router(reflections.router)
