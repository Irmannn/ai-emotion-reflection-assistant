from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Emotion Reflection Assistant API",
    description="FastAPI backend for the AI emotion reflection assistant MVP.",
    version="0.1.0",
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
