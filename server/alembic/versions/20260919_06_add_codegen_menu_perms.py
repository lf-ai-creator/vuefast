"""add code generator menu permissions

Revision ID: 20260919_06
Revises: 20260919_05
Create Date: 2026-09-19

代码生成接口使用 sys:codegen:list / sys:codegen:update 做权限校验，
但初始菜单数据里只有菜单 201（代码生成页面），没有任何按钮权限，
导致非超管角色即使能看到代码生成页面，保存/删除配置也会返回 403。
这里补齐按钮权限并授予管理员角色（role_id = 2）。
"""

from alembic import op

revision = "20260919_06"
down_revision = "20260919_05"
branch_labels = None
depends_on = None

# (菜单ID, 权限标识, 名称, 排序)
_PERMS = [
    (20101, "sys:codegen:list", "代码生成查询", 1),
    (20102, "sys:codegen:update", "代码生成配置", 2),
]


def upgrade() -> None:
    for menu_id, perm, name, sort in _PERMS:
        op.execute(
            f"""
            INSERT INTO sys_menu (id, parent_id, tree_path, name, type, route_name, route_path, component,
                                  perm, keep_alive, visible, sort, icon, create_time, update_time)
            SELECT {menu_id}, 201, '0,2,201', '{name}', 'B', NULL, '', NULL, '{perm}', 0, 1, {sort}, '',
                   now(), now()
            WHERE EXISTS (SELECT 1 FROM sys_menu WHERE id = 201)
              AND NOT EXISTS (SELECT 1 FROM sys_menu WHERE perm = '{perm}')
            """  # noqa: S608 - 常量拼接，无外部输入
        )
        op.execute(
            f"""
            INSERT INTO sys_role_menu (role_id, menu_id)
            SELECT 2, id FROM sys_menu WHERE perm = '{perm}'
            ON CONFLICT DO NOTHING
            """  # noqa: S608 - 常量拼接，无外部输入
        )


def downgrade() -> None:
    perms = ", ".join(f"'{perm}'" for _, perm, _, _ in _PERMS)
    # noqa: S608 - perms 来自本模块常量，无外部输入
    op.execute(f"DELETE FROM sys_role_menu WHERE menu_id IN (SELECT id FROM sys_menu WHERE perm IN ({perms}))")  # noqa: S608
    op.execute(f"DELETE FROM sys_menu WHERE perm IN ({perms})")  # noqa: S608
