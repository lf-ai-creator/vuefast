"""管理操作必须撤销旧会话，避免禁用后继续访问。"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.system.role.service import RoleService
from app.system.user.service import UserService


@pytest.mark.anyio
@pytest.mark.parametrize(
    "method,args", [("update_status", (10, 0)), ("reset_password", (10, "new-password")), ("delete", ("10",))]
)
async def test_user_management_revokes_sessions(monkeypatch, method, args):
    manager = AsyncMock()
    monkeypatch.setattr("app.system.user.service.get_token_manager", AsyncMock(return_value=manager))
    monkeypatch.setattr("app.system.user.service.hash_password", lambda password: "hashed")
    db = AsyncMock()
    db.execute.return_value = Mock(scalar_one_or_none=Mock(return_value=SimpleNamespace(id=10)))
    await getattr(UserService(db), method)(*args)
    manager.invalidate_user_sessions.assert_awaited_once_with(10)


@pytest.mark.anyio
@pytest.mark.parametrize("method,args", [("update_status", (7, 0)), ("assign_menus", (7, [1, 2])), ("delete", ("7",))])
async def test_role_management_revokes_sessions(method, args):
    db = AsyncMock()
    db.execute.return_value = Mock(scalar_one_or_none=Mock(return_value=SimpleNamespace(id=7)))
    service = RoleService(db)
    service._invalidate_role_users_sessions = AsyncMock()
    await getattr(service, method)(*args)
    service._invalidate_role_users_sessions.assert_awaited_once_with(7)
