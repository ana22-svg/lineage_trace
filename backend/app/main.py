from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
import logging
from app.api import channels, ingest, lineage, watchlists, clusters, diffs, metrics, topology
from app.database import check_database
from app.api.auth import require_api_key

app = FastAPI(title="ClaimTrace API", version="2.0")
logger = logging.getLogger(__name__)

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

@app.get("/health")
async def health_check():
    try:
        await check_database()
        return {"status": "healthy", "database": "ready"}
    except Exception:
        return {"status": "degraded", "database": "unavailable"}
