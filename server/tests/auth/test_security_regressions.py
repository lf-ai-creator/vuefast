"""认证与权限安全回归，不访问真实用户或签发真实令牌。"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.schemas import SysUserDetails
from app.auth.service import AuthService
from app.captcha.service import CaptchaService
from app.dependencies import PermissionChecker, get_current_user
from app.exceptions import BusinessException
from app.tool.wxma.service import WxMaAuthService


@pytest.mark.anyio
@pytest.mark.parametrize(
    "payload",
    [
        {"username": "admin", "password": "test"},
        {"username": "admin", "password": "test", "captchaId": "id", "captchaCode": ""},
    ],
)
async def test_login_requires_captcha(async_client, payload):
    response = await async_client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_invalid_captcha_never_checks_password(async_client, monkeypatch):
    monkeypatch.setattr(CaptchaService, "verify", AsyncMock(return_value=False))
    password_login = AsyncMock()
    monkeypatch.setattr(AuthService, "login", password_login)
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin",
            "password": "test",
            "captchaId": "id",
            "captchaCode": "wrong",
        },
    )
    assert response.status_code == 400
    password_login.assert_not_awaited()


@pytest.mark.anyio
async def test_refresh_token_accepts_json_body(async_client, monkeypatch):
    refresh = AsyncMock(return_value={"accessToken": "new", "refreshToken": "new-refresh", "expiresIn": 100})
    monkeypatch.setattr(AuthService, "refresh_token", refresh)
    response = await async_client.post("/api/v1/auth/refresh-token", json={"refreshToken": "old"})
    assert response.status_code == 200
    refresh.assert_awaited_once_with("old")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "method,args",
    [
        ("login_by_sms", ("13800138000", "123456")),
        ("send_sms_code", ("13800138000",)),
        ("silent_login", ("fake-code",)),
        ("phone_login", (SimpleNamespace(loginCode="fake", phoneCode="fake"),)),
        ("bind_mobile", (SimpleNamespace(openid="fake", mobile="13800138000", smsCode="123456"),)),
    ],
)
async def test_unconfigured_login_fails_closed(method, args):
    db = Mock()
    service = AuthService(db) if method in {"login_by_sms", "send_sms_code"} else WxMaAuthService(db)
    with pytest.raises(HTTPException) as error:
        await getattr(service, method)(*args)
    assert error.value.status_code == 501
    assert not db.mock_calls


@pytest.mark.anyio
@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/logs/analytics/overview",
        "/api/v1/logs/analytics/trend",
        "/api/v1/configs/private-key/value",
        "/api/v1/dicts/options",
        "/api/v1/codegen/table",
    ],
)
async def test_metadata_requires_authentication(async_client, path):
    assert (await async_client.get(path)).status_code == 401


@pytest.mark.anyio
async def test_legacy_admin_claim_does_not_bypass_permissions():
    manager = AsyncMock()
    manager.parse_token.return_value = SysUserDetails(userId=2, roles={"ADMIN"}, isRoot=True)
    user = await get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials="test"), manager)
    assert not user.isRoot
    db = AsyncMock()
    db.execute.return_value = Mock(scalar=Mock(return_value=None))
    with pytest.raises(BusinessException):
        await PermissionChecker("sys:user:delete")(user, db)


@pytest.mark.anyio
async def test_root_role_bypasses_permission_query():
    db = AsyncMock()
    user = SysUserDetails(userId=1, roles={"ROOT"})
    assert await PermissionChecker("sys:user:delete")(user, db) is user
    db.execute.assert_not_awaited()
