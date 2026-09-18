"""字典字段映射与分页响应的回归测试，无需连接数据库。"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.system.dict.schemas import DictItemOptionVO, DictItemUpdate, DictItemVO, DictQuery, DictUpdate, DictVO
from app.system.dict.service import DictService


def test_dict_orm_mapping_and_frontend_input():
    obj = SimpleNamespace(id=1, dict_code="gender", name="性别", status=1, remark=None)
    for schema in (DictUpdate, DictVO):
        result = schema.model_validate(obj).model_dump(mode="json", by_alias=True)
        assert result["dictCode"] == "gender"
        assert "dict_code" not in result
    assert DictUpdate(id="1", dictCode="gender", name="性别").dictCode == "gender"


def test_dict_item_mapping_preserves_tag_type():
    obj = SimpleNamespace(
        id=1, dict_code="gender", value="1", label="男", tag_type="P", status=1, sort=2, remark=None
    )
    for schema in (DictItemUpdate, DictItemVO, DictItemOptionVO):
        result = schema.model_validate(obj).model_dump(mode="json", by_alias=True)
        assert result["tagType"] == "P"
        assert "tag_type" not in result
    assert DictItemUpdate(id=1, dictCode="gender", value="1", label="男", tagType="S").tagType == "S"


@pytest.mark.asyncio
async def test_dict_item_page_filters_and_paginates():
    item = SimpleNamespace(id=3, dict_code="gender", value="1", label="男", tag_type="P", status=1, sort=0)
    count_result = MagicMock()
    count_result.scalar.return_value = 3
    rows = MagicMock()
    rows.scalars.return_value.all.return_value = [item]
    db = AsyncMock()
    db.execute.side_effect = [count_result, rows]
    page = await DictService(db).get_item_page("gender", DictQuery(pageNum=2, pageSize=1, keywords="男"))
    result = page.model_dump(mode="json", by_alias=True)
    assert result["total"] == 3
    assert result["list"][0]["dictCode"] == "gender"
    assert result["pageNum"] == 2
    statement = db.execute.call_args_list[1].args[0]
    params = statement.compile().params
    assert "gender" in params.values()
    assert "%男%" in params.values()
    assert statement._offset_clause.value == 1
    assert statement._limit_clause.value == 1
