"""add independent query and list display names

Revision ID: 20260919_04
Revises: 20260919_03
Create Date: 2026-09-19
"""

from alembic import op

revision = "20260919_04"
down_revision = "20260919_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE gen_table_column ADD COLUMN IF NOT EXISTS query_name VARCHAR(100)")
    op.execute("ALTER TABLE gen_table_column ADD COLUMN IF NOT EXISTS list_name VARCHAR(100)")
    op.execute("UPDATE gen_table_column SET query_name = field_comment WHERE query_name IS NULL")
    op.execute("UPDATE gen_table_column SET list_name = field_comment WHERE list_name IS NULL")
    op.execute("COMMENT ON COLUMN gen_table_column.query_name IS '查询条件名称'")
    op.execute("COMMENT ON COLUMN gen_table_column.list_name IS '列表字段名称'")


def downgrade() -> None:
    op.execute("ALTER TABLE gen_table_column DROP COLUMN IF EXISTS list_name")
    op.execute("ALTER TABLE gen_table_column DROP COLUMN IF EXISTS query_name")
