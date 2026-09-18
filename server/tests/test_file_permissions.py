"""文件删除归属校验，不连接对象存储。"""

import pytest

from app.auth.schemas import SysUserDetails
from app.config import settings
from app.exceptions import BusinessException
from app.tool.file.router import _object_name_for_delete


@pytest.fixture(autouse=True)
def storage_config(monkeypatch):
    monkeypatch.setattr(settings, "S3_ENDPOINT", "storage.example.com:9000")
    monkeypatch.setattr(settings, "S3_BUCKET", "public")
    monkeypatch.setattr(settings, "S3_SECURE", False)


def test_user_can_delete_own_file():
    user = SysUserDetails(userId=9, roles={"MEMBER"})
    assert (
        _object_name_for_delete("http://storage.example.com:9000/public/20260919/9/a.jpg", user) == "20260919/9/a.jpg"
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://foreign.example.com/public/20260919/9/a.jpg",
        "http://storage.example.com:9000/public/20260919/10/a.jpg",
        "http://storage.example.com:9000/public/20260919/a.jpg",
        "http://storage.example.com:9000/public/20260919/9/%2e%2e/a.jpg",
    ],
)
def test_user_cannot_delete_foreign_or_invalid_file(url):
    with pytest.raises(BusinessException):
        _object_name_for_delete(url, SysUserDetails(userId=9, roles={"MEMBER"}))


def test_admin_can_delete_legacy_file():
    assert (
        _object_name_for_delete(
            "http://storage.example.com:9000/public/20260919/a.jpg", SysUserDetails(userId=2, roles={"ADMIN"})
        )
        == "20260919/a.jpg"
    )
