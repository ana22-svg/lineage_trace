from fastapi import FastAPI, Depends
from app.api import channels, ingest, lineage, watchlists, clusters, diffs, metrics, topology
from app.database import check_database
from app.api.auth import require_api_key

app = FastAPI(title="ClaimTrace API", version="2.0")

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
