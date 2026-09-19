"""add code generator delete settings

Revision ID: 20260919_03
Revises: 20260919_02
Create Date: 2026-09-19
"""

from alembic import op

revision = "20260919_03"
down_revision = "20260919_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE gen_table ADD COLUMN IF NOT EXISTS delete_enabled SMALLINT NOT NULL DEFAULT 1")
    op.execute("ALTER TABLE gen_table ADD COLUMN IF NOT EXISTS delete_mode VARCHAR(20) NOT NULL DEFAULT 'logical'")
    op.execute("ALTER TABLE gen_table ADD COLUMN IF NOT EXISTS delete_type VARCHAR(20) NOT NULL DEFAULT 'single_batch'")
    op.execute("COMMENT ON COLUMN gen_table.delete_enabled IS '是否允许删除'")
    op.execute("COMMENT ON COLUMN gen_table.delete_mode IS '删除方式 logical/physical'")
    op.execute("COMMENT ON COLUMN gen_table.delete_type IS '删除类型 single_batch/single/batch'")


def downgrade() -> None:
    op.execute("ALTER TABLE gen_table DROP COLUMN IF EXISTS delete_type")
    op.execute("ALTER TABLE gen_table DROP COLUMN IF EXISTS delete_mode")
    op.execute("ALTER TABLE gen_table DROP COLUMN IF EXISTS delete_enabled")
