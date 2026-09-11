from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.cluster import TopologyLabels
from app import crud

router = APIRouter(prefix="/api/clusters", tags=["Topology"])

@router.get("/{cluster_id}/topology", response_model=TopologyLabels)
async def get_cluster_topology(cluster_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns both the internal graph-theoretic label and the mapped 
    external pitch-vocabulary label[cite: 2].
    """
    cluster = await crud.get_cluster(db, cluster_id)
    if cluster is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Cluster not found")
    return {"internal": cluster.topology_label_internal, "external": cluster.topology_label_external}
