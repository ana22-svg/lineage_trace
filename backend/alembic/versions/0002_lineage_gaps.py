"""Store probable missing hops separately from confirmed edges."""
from alembic import op
from app.models.lineage_gap import LineageGap

revision = "0002_lineage_gaps"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None

def upgrade():
    LineageGap.__table__.create(op.get_bind(), checkfirst=True)

def downgrade():
    LineageGap.__table__.drop(op.get_bind(), checkfirst=True)
