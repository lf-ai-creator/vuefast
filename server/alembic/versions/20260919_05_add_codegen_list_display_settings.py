"""add code generator list display settings

Revision ID: 20260919_05
Revises: 20260919_04
Create Date: 2026-09-19
"""

from alembic import op

revision = "20260919_05"
down_revision = "20260919_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE gen_table_column ADD COLUMN IF NOT EXISTS list_width INTEGER")
    op.execute("ALTER TABLE gen_table_column ADD COLUMN IF NOT EXISTS list_ellipsis SMALLINT NOT NULL DEFAULT 1")
    op.execute("COMMENT ON COLUMN gen_table_column.list_width IS '列表列宽'")
    op.execute("COMMENT ON COLUMN gen_table_column.list_ellipsis IS '列表自动省略'")


def downgrade() -> None:
    op.execute("ALTER TABLE gen_table_column DROP COLUMN IF EXISTS list_ellipsis")
    op.execute("ALTER TABLE gen_table_column DROP COLUMN IF EXISTS list_width")
