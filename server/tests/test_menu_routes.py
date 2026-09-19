"""隐藏菜单的路由注册与角色过滤回归测试。"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.system.menu.schemas import MenuUpdate
from app.system.menu.service import MenuService


@pytest.mark.asyncio
@pytest.mark.parametrize("is_root", [True, False])
async def test_hidden_menu_registered_with_role_filter(is_root):
    hidden_menu = SimpleNamespace(
        id=106,
        parent_id=0,
        name="字典数据",
        type="M",
        route_name="DictItem",
        route_path="/system/dict-item",
        component="system/dict/dict-item",
        visible=0,
        icon="",
        always_show=0,
        keep_alive=1,
        redirect=None,
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


@pytest.mark.asyncio
async def test_menu_form_normalizes_legacy_nullable_fields_and_params():
    menu = SimpleNamespace(
        id=106,
        parent_id=1,
        name="字典数据",
        type="M",
        route_name="DictItem",
        route_path="dict-item",
        component="system/dict/dict-item",
        external_url=None,
        perm=None,
        always_show=None,
        keep_alive=None,
        visible=1,
        sort=None,
        icon="",
        redirect=None,
        params={"dictCode": "notice_type", "title": "通知类型"},
    )
    result = MagicMock()
    result.scalar_one_or_none.return_value = menu
    db = AsyncMock()
    db.execute.return_value = result

    form = await MenuService(db).get_menu_form(106)

    assert form.alwaysShow == 0
    assert form.keepAlive == 0
    assert form.sort == 0
    assert [item.model_dump() for item in form.params] == [
        {"key": "dictCode", "value": "notice_type"},
        {"key": "title", "value": "通知类型"},
    ]


def test_menu_payload_params_are_stored_as_json_object():
    form = MenuUpdate(
        id=106,
        parentId=1,
        name="字典数据",
        type="M",
        params=[{"key": "dictCode", "value": "notice_type"}],
    )
    assert MenuService._params_to_dict(form.params) == {"dictCode": "notice_type"}


@pytest.mark.asyncio
async def test_parent_options_keep_nested_parents_and_string_ids():
    rows = [
        SimpleNamespace(id=1, parent_id=0, name="系统管理", type="C"),
        SimpleNamespace(id=10, parent_id=1, name="二级目录", type="C"),
        SimpleNamespace(id=101, parent_id=10, name="用户管理", type="M"),
    ]
    result = MagicMock()
    result.__iter__.return_value = iter(rows)
    db = AsyncMock()
    db.execute.return_value = result

    options = await MenuService(db).get_options(only_parent=True)

    assert options[0]["value"] == "1"
    assert options[0]["children"][0]["value"] == "10"
    assert options[0]["children"][0]["children"][0]["value"] == "101"
    statement = str(db.execute.call_args.args[0])
    assert "sys_menu.type !=" in statement
    assert "sys_menu.parent_id =" not in statement
