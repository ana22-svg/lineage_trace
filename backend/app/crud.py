from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import MonitoredChannel
from app.models.cluster import ClaimCluster
from app.models.message import RawMessage
from app.models.edge import LineageEdge
from app.models.diff import MutationDiff
from app.models.metric import MetricSnapshot
from app.models.watchlist import WatchCondition, Alert

async def get_channel(db, channel_id):
    return await db.get(MonitoredChannel, channel_id)

async def create_channel(db, platform_channel_id, display_name, added_by=None):
    obj = MonitoredChannel(platform_channel_id=platform_channel_id, display_name=display_name, added_by=added_by, created_at=datetime.now(timezone.utc))
    db.add(obj); await db.commit(); await db.refresh(obj); return obj

async def list_channels(db):
    result = await db.execute(
        select(MonitoredChannel, func.max(RawMessage.timestamp).label("last_ingested_at"))
        .outerjoin(RawMessage, RawMessage.channel_id == MonitoredChannel.id)
        .group_by(MonitoredChannel.id)
        .order_by(MonitoredChannel.display_name)
    )
    return [
        {
            "id": channel.id,
            "platform_channel_id": channel.platform_channel_id,
            "display_name": channel.display_name,
            "is_active": channel.is_active,
            "added_by": channel.added_by,
            "created_at": channel.created_at,
            "last_ingested_at": last_ingested_at,
        }
        for channel, last_ingested_at in result.all()
    ]

async def set_channel_active(db, channel_id, active):
    obj = await db.get(MonitoredChannel, channel_id)
    if obj is None: return None
    obj.is_active = active; await db.commit(); await db.refresh(obj); return obj

async def list_clusters(db, offset=0, limit=50):
    return list((await db.scalars(select(ClaimCluster).order_by(ClaimCluster.last_seen.desc()).offset(offset).limit(limit))).all())

async def get_cluster(db, cluster_id): return await db.get(ClaimCluster, cluster_id)

async def get_message_by_source(db, source, source_id):
    return await db.scalar(select(RawMessage).where(RawMessage.source == source, RawMessage.source_id == source_id))

async def cluster_messages(db, cluster_id):
    return list((await db.scalars(select(RawMessage).where(RawMessage.cluster_id == cluster_id).order_by(RawMessage.timestamp))).all())

async def cluster_edges(db, cluster_id):
    return list((await db.scalars(select(LineageEdge).where(LineageEdge.cluster_id == cluster_id))).all())

async def edge_diff(db, edge_id):
    return await db.scalar(select(MutationDiff).where(MutationDiff.edge_id == edge_id))

async def create_watch_condition(db, data):
    obj = WatchCondition(**data, created_at=datetime.now(timezone.utc)); db.add(obj); await db.commit(); await db.refresh(obj); return obj

async def list_alerts(db, offset=0, limit=50):
    return list((await db.scalars(select(Alert).order_by(Alert.created_at.desc()).offset(offset).limit(limit))).all())
