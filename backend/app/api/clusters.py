from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.cluster import ClusterResponse
from app import crud

router = APIRouter(prefix="/api/clusters", tags=["Clusters"])

@router.get("/", response_model=List[ClusterResponse])
async def list_clusters(page: int = 1, page_size: int = 50, db: AsyncSession = Depends(get_db)):
    """Retrieves all active claim lineages."""
    # return await crud.get_all_clusters(db)
    page_size = min(max(page_size, 1), 100)
    clusters = await crud.list_clusters(db, (max(page, 1)-1)*page_size, page_size)
    return [
        {
            "id": cluster.id,
            "member_count": cluster.member_count,
            "topology": {
                "internal": cluster.topology_label_internal,
                "external": cluster.topology_label_external,
            },
            "first_seen": cluster.first_seen,
            "last_seen": cluster.last_seen,
        }
        for cluster in clusters
    ]

@router.get("/{cluster_id}", response_model=ClusterResponse)
async def get_cluster(cluster_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves high-level metadata for a single cluster."""
    # return await crud.get_cluster(db, cluster_id)
    result = await crud.get_cluster(db, cluster_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Cluster not found")
    return {"id": result.id, "member_count": result.member_count, "topology": {"internal": result.topology_label_internal, "external": result.topology_label_external}, "first_seen": result.first_seen, "last_seen": result.last_seen}
