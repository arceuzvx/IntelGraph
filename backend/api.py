"""
IntelGraph — FastAPI application entry point.

Mounts the API routes and serves the frontend as static files.

Usage:
    cd backend
    uvicorn api:app --reload --port 8000

The frontend is served from ../frontend/ at the root path.
API endpoints are under /api/.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routes import router as search_router
from create_collection import ensure_collection
from vectorai_connection import VectorAIConnection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Keep one VectorAI connection open while this API worker is running."""
    connection = VectorAIConnection()
    client = connection.connect()
    ensure_collection(client)
    app.state.vectorai_client = client
    try:
        yield
    finally:
        connection.close()

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="IntelGraph",
    description="Semantic Cyber Threat Intelligence Search Engine",
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
app.include_router(search_router)

# ---------------------------------------------------------------------------
# Frontend static files
# ---------------------------------------------------------------------------
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/", include_in_schema=False)
def serve_frontend() -> FileResponse:
    """Serve the frontend index.html at the root path."""
    return FileResponse(FRONTEND_DIR / "index.html")


# Mount static assets (CSS, JS) — must come after explicit routes
app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static",
)
