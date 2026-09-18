"""Initial Lineage Trace schema."""
from alembic import op
from app.database import Base
from app.models import message, cluster, edge, diff, coordination, watchlist, channel, metric

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    Base.metadata.create_all(bind=op.get_bind())

def downgrade():
    Base.metadata.drop_all(bind=op.get_bind())
