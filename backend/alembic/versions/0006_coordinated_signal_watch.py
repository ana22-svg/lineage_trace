"""Watch coordinated signals."""
from alembic import op

revision = "0006_coordinated_signal_watch"
down_revision = "0005_metric_created_at"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE watch_condition_enum ADD VALUE IF NOT EXISTS 'coordinated_signal'")


def downgrade():
    # PostgreSQL enums cannot safely remove a value in place; retained on downgrade.
    pass
