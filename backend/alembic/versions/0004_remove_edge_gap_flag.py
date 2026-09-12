"""Remove the obsolete gap marker from confirmed lineage edges."""
from alembic import op
import sqlalchemy as sa

revision = "0004_remove_edge_gap_flag"
down_revision = "0003_p1_integrity"
branch_labels = None
depends_on = None

def upgrade():
    inspector = sa.inspect(op.get_bind())
    if "is_flagged_gap" in {c["name"] for c in inspector.get_columns("lineage_edges")}:
        op.drop_column("lineage_edges", "is_flagged_gap")

def downgrade():
    op.add_column("lineage_edges", sa.Column("is_flagged_gap", sa.Boolean(), nullable=False, server_default=sa.false()))
