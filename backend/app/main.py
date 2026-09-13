import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
from app.api import channels, ingest, lineage, watchlists, clusters, diffs, metrics, topology
from app.database import check_database
from app.api.auth import require_api_key

app = FastAPI(title="ClaimTrace API", version="2.0")
logger = logging.getLogger(__name__)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    logger.exception("unhandled_api_error", extra={"path": request.url.path})
    return JSONResponse(status_code=500, content={"error": "internal_server_error", "detail": "An unexpected error occurred"})

app.include_router(channels.router, dependencies=[Depends(require_api_key)])
app.include_router(ingest.router, dependencies=[Depends(require_api_key)])
app.include_router(lineage.router, dependencies=[Depends(require_api_key)])
app.include_router(watchlists.router, dependencies=[Depends(require_api_key)])
app.include_router(clusters.router, dependencies=[Depends(require_api_key)])
app.include_router(diffs.router, dependencies=[Depends(require_api_key)])
app.include_router(metrics.router, dependencies=[Depends(require_api_key)])
app.include_router(topology.router, dependencies=[Depends(require_api_key)])

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    async def frontend_index():
        return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/health")
async def health_check():
    try:
        await check_database()
        return {"status": "healthy", "database": "ready"}
    except Exception:
        return {"status": "degraded", "database": "unavailable"}
