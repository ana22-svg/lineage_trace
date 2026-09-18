from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.lineage import LineageGraphResponse
from app import crud
from sqlalchemy import select
from app.models.message import RawMessage
from app.models.edge import LineageEdge

router = APIRouter(prefix="/api/clusters", tags=["Lineage"])

@router.get("/{cluster_id}/messages")
async def list_cluster_messages(cluster_id: str, page: int = 1, page_size: int = 50, db: AsyncSession = Depends(get_db)):
    if await crud.get_cluster(db, cluster_id) is None:
        raise HTTPException(404, "Cluster not found")
    page_size = min(max(page_size, 1), 100)
    rows = list((await db.scalars(select(RawMessage).where(RawMessage.cluster_id == cluster_id).order_by(RawMessage.timestamp).offset((max(page, 1)-1)*page_size).limit(page_size))).all())
    return [{"id": str(row.id), "text": row.text, "language": row.language, "timestamp": row.timestamp, "source": row.source} for row in rows]

@router.get("/{cluster_id}/edges")
async def list_cluster_edges(cluster_id: str, page: int = 1, page_size: int = 50, db: AsyncSession = Depends(get_db)):
    if await crud.get_cluster(db, cluster_id) is None:
        raise HTTPException(404, "Cluster not found")
    page_size = min(max(page_size, 1), 100)
    rows = list((await db.scalars(select(LineageEdge).where(LineageEdge.cluster_id == cluster_id).order_by(LineageEdge.created_at).offset((max(page, 1)-1)*page_size).limit(page_size))).all())
    return [{"id": str(row.id), "parent_message_id": str(row.parent_message_id), "child_message_id": str(row.child_message_id), "similarity_score": row.similarity_score, "similarity_decay": row.similarity_decay} for row in rows]

@router.get("/{cluster_id}/lineage", response_model=LineageGraphResponse)
async def get_cluster_lineage(cluster_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns the complete lineage graph structure, metrics series, 
    and dual topology labels for frontend rendering.
    """
    # cluster = crud.get_cluster(db, cluster_id)
    # nodes = crud.get_cluster_nodes(db, cluster_id)
    # edges = crud.get_cluster_edges(db, cluster_id)
    # r_claim_series = crud.get_r_claim_series(db, cluster_id)
    # debunk_lag = crud.get_debunk_lag(db, cluster_id)
    
    cluster = await crud.get_cluster(db, cluster_id)
    if cluster is None:
        raise HTTPException(404, "Cluster not found")
    nodes = await crud.cluster_messages(db, cluster_id)
    edges = await crud.cluster_edges(db, cluster_id)
    return {
        "cluster_id": cluster_id,
        "topology": {
            "internal": cluster.topology_label_internal,
            "external": cluster.topology_label_external
        },
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": [{"id": str(n.id), "text": n.text, "timestamp": n.timestamp, "language": n.language, "source": n.source, "source_id": n.source_id, "author_id": n.author_id, "channel_id": str(n.channel_id) if n.channel_id else None, "metadata_json": n.metadata_json or {}} for n in nodes],
        "edges": [{"id": str(e.id), "parent_message_id": str(e.parent_message_id), "child_message_id": str(e.child_message_id), "similarity": e.similarity_score, "decay": e.similarity_decay} for e in edges],
        "r_claim_series": [],
        "debunk_lag": {
            "has_debunk": False,
            "debunk_lag_hours": None,
            "estimation_method": None
        }
    }
