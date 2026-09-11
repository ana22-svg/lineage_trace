from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.diff import MutationDiffResponse
from app import crud

router = APIRouter(prefix="/api/edges", tags=["Mutation Diffs"])

@router.get("/{edge_id}/diff", response_model=MutationDiffResponse)
async def get_edge_diff(edge_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves the structured mutation diff for a specific hop in the lineage."""
    # return await crud.get_diff(db, edge_id)
    result = await crud.edge_diff(db, edge_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Diff not found")
    return {"edge_id": result.edge_id, **result.diff_json, "danger_score": result.danger_score, "distortion_magnitude": result.distortion_magnitude, "downstream_reach": result.downstream_reach}
