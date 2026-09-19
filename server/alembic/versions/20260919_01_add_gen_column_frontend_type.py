"""add frontend type override to code generation columns

Revision ID: 20260919_01
Revises:
Create Date: 2026-09-19
"""

from alembic import op

revision = "20260919_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE gen_table_column ADD COLUMN IF NOT EXISTS frontend_type VARCHAR(50)")
    op.execute("COMMENT ON COLUMN gen_table_column.frontend_type IS '前端类型'")


def downgrade() -> None:
    op.execute("ALTER TABLE gen_table_column DROP COLUMN IF EXISTS frontend_type")
