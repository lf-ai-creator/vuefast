"""通知表单、个人通知过滤与路由回归测试。"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.routing import Match

from app.exceptions import BusinessException
from app.system.notice.router import NoticeForm, NoticeQuery, NoticeService, router


def test_edit_form_preserves_id_targets_and_status():
    obj = SimpleNamespace(
        id=123, title="公告", content="内容", type=1, level="L", target_type=2,
        target_user_ids="1,2", publish_status=-1,
    )
    form = NoticeForm.model_validate(obj)
    result = form.model_dump(mode="json", by_alias=True)
    assert result["id"] == "123"
    assert result["targetType"] == 2
    assert result["targetUsers"] == "1,2"
    assert result["status"] == -1
    assert NoticeForm(**{**result, "targetUserIds": [1, 2]}).targetUserIds == [1, 2]


def test_read_all_and_detail_routes_match():
    scope = {"type": "http", "method": "PUT", "path": "/api/v1/notices/read-all", "root_path": ""}
    matched = next(route for route in router.routes if route.matches(scope)[0] == Match.FULL)
    assert matched.path == "/api/v1/notices/read-all"
    assert any(route.path == "/api/v1/notices/{notice_id}/detail" for route in router.routes)


@pytest.mark.asyncio
async def test_my_notices_filter_by_recipient_read_status_and_title():
    count = MagicMock()
    count.scalar.return_value = 0
    db = AsyncMock()
    db.execute.side_effect = [count, []]
    await NoticeService(db).get_my_page(NoticeQuery(isRead=0, title="公告"), 123)
    for call in db.execute.call_args_list:
        statement = call.args[0]
        sql = str(statement)
        assert "sys_user_notice.user_id =" in sql
        assert "sys_user_notice.is_read =" in sql
        assert "sys_user_notice.is_deleted =" in sql
        assert "LEFT OUTER JOIN" not in sql
        assert 123 in statement.compile().params.values()
        assert "%公告%" in statement.compile().params.values()


@pytest.mark.asyncio
async def test_published_notice_cannot_be_edited():
    db = AsyncMock()
    db.get.return_value = SimpleNamespace(publish_status=1)
    form = NoticeForm(title="公告", content="内容", type=1, level="L", targetType=1)
    with pytest.raises(BusinessException):
        await NoticeService(db).update(1, form, 123)
    db.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_non_recipient_cannot_view_targeted_notice():
    db = AsyncMock()
    db.get.return_value = SimpleNamespace(is_deleted=0, publish_status=1, create_by=1, publisher_id=1)
    rows = MagicMock()
    rows.scalar.return_value = None
    db.execute.return_value = rows
    with pytest.raises(BusinessException):
        await NoticeService(db).get_by_id(1, 123)
