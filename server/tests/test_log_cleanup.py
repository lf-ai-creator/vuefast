"""管理员日志清理权限、边界与审计回归测试。"""

from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.auth.schemas import SysUserDetails
from app.database import get_db
from app.dependencies import get_current_user
from app.main import create_app
from app.system.log.router import LogService


@pytest.mark.asyncio
async def test_history_delete_uses_exclusive_cutoff():
    db = AsyncMock()
    result = MagicMock()
    result.rowcount = 3
    db.execute.return_value = result
    assert await LogService(db).clear_history(date(2020, 1, 2)) == 3
    statement = db.execute.call_args.args[0]
    assert "sys_log.create_time <" in str(statement)
    assert list(statement.compile().params.values()) == [datetime(2020, 1, 2)]


@pytest.mark.asyncio
@pytest.mark.parametrize("role,expected", [("ROOT", 200), ("ADMIN", 200), ("EMPLOYEE", 403)])
async def test_cleanup_endpoint_permission_and_audit(monkeypatch, role, expected):
    app = create_app()
    db = AsyncMock()
    result = MagicMock()
    result.rowcount = 3
    db.execute.return_value = result
    writer = AsyncMock()
    monkeypatch.setattr("app.system.log.operation_log.write_operation_log", writer)

    async def current_user():
        return SysUserDetails(userId=1, username="test", roles={role})

    async def database():
        yield db

    app.dependency_overrides[get_current_user] = current_user
    app.dependency_overrides[get_db] = database
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete("/api/v1/logs/history", params={"beforeDate": "2020-01-02"})
    assert response.status_code == expected
    if expected == 200:
        assert response.json()["data"]["deletedCount"] == 3
        db.commit.assert_awaited_once()
        assert "2020-01-02" in writer.call_args.kwargs["content"]
        assert writer.call_args.kwargs["operator_name"] == "test"
    else:
        db.execute.assert_not_awaited()
        db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_future_cutoff_cannot_clear_current_logs():
    from fastapi import HTTPException

    db = AsyncMock()
    with pytest.raises(HTTPException) as error:
        await LogService(db).clear_history(date.today() + timedelta(days=1))
    assert error.value.status_code == 422
    db.execute.assert_not_awaited()
