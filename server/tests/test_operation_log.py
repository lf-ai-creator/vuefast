"""操作日志写入与展示回归测试。"""

from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.requests import Request

from app.response import Result, ResultCode
from app.system.log.models import SysLog
from app.system.log.operation_log import operation_log
from app.system.log.router import LogQuery, LogService, LogVO


def test_log_fields_and_timestamp():
    obj = SimpleNamespace(
        id=1, request_uri="/api/v1/notices", request_method="POST", operator_id=1,
        operator_name="admin", action_type=3, execution_time=42, error_msg="failure",
        create_time=datetime(2026, 9, 19, 12, 30),
    )
    result = LogVO.model_validate(obj).model_dump(mode="json", by_alias=True)
    assert result["requestUri"] == "/api/v1/notices"
    assert result["operatorName"] == "admin"
    assert result["executionTime"] == 42
    assert result["createTime"] == "2026-09-19 12:30:00"
    assert SysLog.__table__.c.create_time.default is not None


@pytest.mark.asyncio
async def test_logging_failure_does_not_break_request(monkeypatch):
    writer = AsyncMock(side_effect=RuntimeError("database unavailable"))
    monkeypatch.setattr("app.system.log.operation_log.write_operation_log", writer)

    @operation_log(title="test")
    async def handler(**kwargs):
        return Result(data=None)

    request = Request({"type": "http", "method": "POST", "path": "/test", "query_string": b"token=secret", "headers": [], "client": None})
    assert (await handler(request=request)).code == ResultCode.SUCCESS
    assert writer.call_args.kwargs["request_uri"] == "/test"
    assert writer.call_args.kwargs["ip"] == ""


@pytest.mark.asyncio
async def test_failed_business_response_recorded(monkeypatch):
    writer = AsyncMock()
    monkeypatch.setattr("app.system.log.operation_log.write_operation_log", writer)

    @operation_log()
    async def handler():
        return Result(code=ResultCode.CAPTCHA_ERROR, msg="验证码错误")

    await handler()
    assert writer.call_args.kwargs["status"] == 0
    assert writer.call_args.kwargs["error_msg"] == "验证码错误"


@pytest.mark.asyncio
async def test_log_date_filter():
    count = MagicMock()
    count.scalar.return_value = 0
    rows = MagicMock()
    rows.scalars.return_value.all.return_value = []
    db = AsyncMock()
    db.execute.side_effect = [count, rows]
    await LogService(db).get_page(LogQuery(createTime=[date(2026, 9, 13), date(2026, 9, 19)]))
    params = db.execute.call_args.args[0].compile().params.values()
    assert datetime(2026, 9, 13) in params
    assert datetime(2026, 9, 20) in params


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "agent,browser,operating_system",
    [
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "Edge", "Windows",
        ),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Safari", "Mac OS X",
        ),
        ("", "Other", "Other"),
    ],
)
async def test_request_browser_and_os_recorded(monkeypatch, agent, browser, operating_system):
    writer = AsyncMock()
    monkeypatch.setattr("app.system.log.operation_log.write_operation_log", writer)

    @operation_log()
    async def handler(**kwargs):
        return Result()

    request = Request({
        "type": "http", "method": "POST", "path": "/test", "query_string": b"",
        "headers": [(b"user-agent", agent.encode())], "client": ("127.0.0.1", 1234),
    })
    await handler(request=request)
    assert writer.call_args.kwargs["browser"].startswith(browser)
    assert writer.call_args.kwargs["os"].startswith(operating_system)
    assert writer.call_args.kwargs["device"]
