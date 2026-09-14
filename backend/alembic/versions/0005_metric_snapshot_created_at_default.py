"""Add a database default for metric snapshot timestamps."""
from alembic import op
import sqlalchemy as sa

revision = "0005_metric_created_at"
down_revision = "0004_remove_edge_gap_flag"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "metric_snapshots",
        "created_at",
        server_default=sa.text("now()"),
    )


def downgrade():
    op.alter_column("metric_snapshots", "created_at", server_default=None)
