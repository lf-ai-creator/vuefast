"""add code generator form settings

Revision ID: 20260919_02
Revises: 20260919_01
Create Date: 2026-09-19
"""

from alembic import op

revision = "20260919_02"
down_revision = "20260919_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE gen_table ADD COLUMN IF NOT EXISTS form_enabled SMALLINT NOT NULL DEFAULT 1")
    op.execute("ALTER TABLE gen_table ADD COLUMN IF NOT EXISTS form_layout VARCHAR(20) NOT NULL DEFAULT 'dialog'")
    op.execute("ALTER TABLE gen_table ADD COLUMN IF NOT EXISTS form_width VARCHAR(20) NOT NULL DEFAULT '600px'")
    op.execute("ALTER TABLE gen_table ADD COLUMN IF NOT EXISTS form_columns SMALLINT NOT NULL DEFAULT 2")
    op.execute("ALTER TABLE gen_table_column ADD COLUMN IF NOT EXISTS is_show_in_create SMALLINT NOT NULL DEFAULT 0")
    op.execute("ALTER TABLE gen_table_column ADD COLUMN IF NOT EXISTS is_show_in_update SMALLINT NOT NULL DEFAULT 0")
    op.execute("UPDATE gen_table_column SET is_show_in_create = is_show_in_form, is_show_in_update = is_show_in_form")


def downgrade() -> None:
    op.execute("ALTER TABLE gen_table_column DROP COLUMN IF EXISTS is_show_in_update")
    op.execute("ALTER TABLE gen_table_column DROP COLUMN IF EXISTS is_show_in_create")
    op.execute("ALTER TABLE gen_table DROP COLUMN IF EXISTS form_columns")
    op.execute("ALTER TABLE gen_table DROP COLUMN IF EXISTS form_width")
    op.execute("ALTER TABLE gen_table DROP COLUMN IF EXISTS form_layout")
    op.execute("ALTER TABLE gen_table DROP COLUMN IF EXISTS form_enabled")
