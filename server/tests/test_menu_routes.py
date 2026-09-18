"""隐藏菜单的路由注册与角色过滤回归测试。"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.system.menu.service import MenuService


@pytest.mark.asyncio
@pytest.mark.parametrize("is_root", [True, False])
async def test_hidden_menu_registered_with_role_filter(is_root):
    hidden_menu = SimpleNamespace(
        id=106, parent_id=0, name="字典数据", type="M", route_name="DictItem",
        route_path="/system/dict-item", component="system/dict/dict-item",
        visible=0, icon="", always_show=0, keep_alive=1, redirect=None,
    )
    rows = MagicMock()
    rows.scalars.return_value.all.return_value = [hidden_menu]
    db = AsyncMock()
    db.execute.return_value = rows
    routes = await MenuService(db).get_routes(roles={"ADMIN"}, is_root=is_root)
    assert routes[0].name == "DictItem"
    assert routes[0].meta["hidden"] is True
    statement = str(db.execute.call_args.args[0])
    where = statement.split("WHERE", 1)[1]
    assert "sys_menu.visible" not in where
    assert "sys_menu.type !=" in where
    if not is_root:
        assert "sys_role_menu" in where
        assert "sys_role.status" in where


@pytest.mark.asyncio
async def test_user_without_roles_gets_no_routes():
    db = AsyncMock()
    assert await MenuService(db).get_routes(roles=set(), is_root=False) == []
    db.execute.assert_not_awaited()
