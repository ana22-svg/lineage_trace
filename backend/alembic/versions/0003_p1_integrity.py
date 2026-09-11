"""P1 integrity fields for idempotency and diff lifecycle."""
from alembic import op
import sqlalchemy as sa

revision = "0003_p1_integrity"
down_revision = "0002_lineage_gaps"
branch_labels = None
depends_on = None

def upgrade():
    inspector = sa.inspect(op.get_bind())
    constraints = {c.get("name") for c in inspector.get_unique_constraints("raw_messages")}
    if "uq_raw_messages_source_source_id" not in constraints:
        op.create_unique_constraint("uq_raw_messages_source_source_id", "raw_messages", ["source", "source_id"])
    columns = {c["name"] for c in inspector.get_columns("mutation_diffs")}
    if "diff_status" not in columns:
        op.add_column("mutation_diffs", sa.Column("diff_status", sa.String(), nullable=True, server_default="pending"))
    op.execute("UPDATE mutation_diffs SET diff_status = 'complete' WHERE diff_status IS NULL")

def downgrade():
    op.drop_column("mutation_diffs", "diff_status")
    op.drop_constraint("uq_raw_messages_source_source_id", "raw_messages", type_="unique")
