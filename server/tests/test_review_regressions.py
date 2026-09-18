"""跨域和表单字段映射回归。"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.auth.schemas import SysUserDetails
from app.config import Settings, settings
from app.exceptions import BusinessException
from app.middleware import setup_cors
from app.system.dept.schemas import DeptUpdate
from app.system.dept.service import DeptService
from app.system.role.data_permission import build_data_scope_filters
from app.system.role.schemas import RoleOptionVO
from app.system.role.service import RoleService
from app.system.user.models import SysUser
from app.system.user.service import UserService
from app.validation import parse_ids


def test_dept_form_preserves_parent_id():
    dept = SimpleNamespace(id=12, name="研发", code="DEV", parent_id=7, sort=1, status=1)
    assert DeptUpdate.model_validate(dept, from_attributes=True).parentId == 7


def test_signing_secret_is_required(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, JWT_SECRET_KEY="short")


def test_role_options_preserve_client_field_names():
    option = RoleOptionVO(id=2, name="管理员")
    assert option.model_dump(mode="json", by_alias=True) == {"value": "2", "label": "管理员"}


def test_missing_data_scope_does_not_grant_all_data():
    filters = build_data_scope_filters(SysUserDetails(userId=9, roles={"MEMBER"}), SysUser.dept_id)
    assert len(filters) == 1
    assert str(filters[0]) == "false"


@pytest.mark.anyio
@pytest.mark.parametrize("parent_id", [7, 8])
async def test_dept_rejects_self_and_descendant(parent_id):
    db = AsyncMock()
    db.get.return_value = SimpleNamespace(id=8, parent_id=7, is_deleted=0)
    with pytest.raises(BusinessException):
        await DeptService(db)._validate_parent(parent_id, dept_id=7)


@pytest.mark.anyio
async def test_dept_rejects_missing_parent():
    db = AsyncMock()
    db.get.return_value = None
    with pytest.raises(BusinessException):
        await DeptService(db)._validate_parent(99)


@pytest.mark.parametrize("value", ["", "abc", "1,", "0", "-1", str(2**63)])
def test_invalid_ids_raise_validation_error(value):
    with pytest.raises(BusinessException) as error:
        parse_ids(value)
    assert error.value.http_status == 422


def test_ids_are_deduplicated():
    assert parse_ids("1, 2,1") == [1, 2]


@pytest.mark.anyio
async def test_admin_cannot_manage_builtin_root():
    db = AsyncMock()
    with pytest.raises(BusinessException):
        await UserService(db).check_management(SysUserDetails(userId=2, roles={"ADMIN"}), target_id=1)
    db.execute.assert_not_awaited()


@pytest.mark.anyio
async def test_admin_cannot_grant_root_role():
    db = AsyncMock()
    db.execute.return_value = Mock(scalar=Mock(return_value=1))
    with pytest.raises(BusinessException):
        await UserService(db).check_management(SysUserDetails(userId=2, roles={"ADMIN"}), role_ids=[1])


@pytest.mark.anyio
async def test_admin_cannot_create_root_role():
    with pytest.raises(BusinessException):
        await RoleService(AsyncMock()).check_management(SysUserDetails(userId=2, roles={"ADMIN"}), new_code="ROOT")


@pytest.mark.anyio
@pytest.mark.parametrize("origin,status", [("https://admin.example.com", 200), ("https://adminXexample.com", 400)])
async def test_cors_exact_origins_and_platform_headers(monkeypatch, origin, status):
    monkeypatch.setattr(settings, "ALLOWED_ORIGINS", "https://admin.example.com,https://other.example.com")
    monkeypatch.setattr(settings, "DEBUG", True)
    app = FastAPI()
    setup_cors(app)
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        response = await client.options(
            "/",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,x-client-platform,x-client-platform-version",
            },
        )
    assert response.status_code == status
    if status == 200:
        assert response.headers["access-control-allow-origin"] == origin
