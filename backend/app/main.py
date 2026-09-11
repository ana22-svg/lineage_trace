from fastapi import FastAPI
from app.api import channels, ingest, lineage, watchlists, clusters, diffs, metrics, topology
from app.database import check_database

app = FastAPI(title="ClaimTrace API", version="2.0")

app.include_router(channels.router)
app.include_router(ingest.router)
app.include_router(lineage.router)
app.include_router(watchlists.router)
app.include_router(clusters.router)
app.include_router(diffs.router)
app.include_router(metrics.router)
app.include_router(topology.router)

@app.get("/health")
async def health_check():
    try:
        await check_database()
        return {"status": "healthy", "database": "ready"}
    except Exception:
        return {"status": "degraded", "database": "unavailable"}
