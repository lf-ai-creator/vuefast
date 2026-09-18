"""配置编辑、缓存同步及输入校验回归测试。"""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import BusinessException
from app.system.config.router import ConfigForm, ConfigService, ConfigVO


def test_config_mapping_retains_edit_id_and_dates():
    obj = SimpleNamespace(
        id=123, config_name="名称", config_key="test.key", config_value="value", remark=None,
        create_time=datetime(2026, 9, 19), update_time=datetime(2026, 9, 19),
    )
    form = ConfigForm.model_validate(obj)
    assert form.model_dump(mode="json")["id"] == "123"
    assert form.configKey == "test.key"
    result = ConfigVO.model_validate(obj).model_dump(mode="json")
    assert result["configValue"] == "value"
    assert result["createTime"] == "2026-09-19 00:00:00"
    assert ConfigForm(configName="名称", configKey="test", configValue="value").configKey == "test"


@pytest.mark.asyncio
async def test_cache_refresh_cleans_managed_old_keys(monkeypatch):
    db = AsyncMock()
    rows = MagicMock()
    rows.all.return_value = [("active", "value", 0), ("deleted", "old", 1)]
    db.execute.return_value = rows
    redis = MagicMock()
    redis.smembers = AsyncMock(return_value={b"config:renamed"})
    pipeline = MagicMock()
    pipeline.__aenter__ = AsyncMock(return_value=pipeline)
    pipeline.__aexit__ = AsyncMock(return_value=False)
    pipeline.execute = AsyncMock()
    redis.pipeline.return_value = pipeline
    monkeypatch.setattr("app.system.config.router.get_redis", AsyncMock(return_value=redis))
    assert await ConfigService(db).refresh_cache() is True
    pipeline.delete.assert_any_call("config:deleted", "config:renamed")
    pipeline.set.assert_called_once_with("config:active", "value")
    pipeline.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_deleted_config_cannot_be_edited():
    db = AsyncMock()
    db.get.return_value = SimpleNamespace(is_deleted=1)
    with pytest.raises(BusinessException):
        await ConfigService(db).get_config_form(1)


@pytest.mark.asyncio
async def test_invalid_delete_ids_are_business_error():
    db = AsyncMock()
    with pytest.raises(BusinessException):
        await ConfigService(db).delete("invalid")
    db.get.assert_not_awaited()


@pytest.mark.asyncio
async def test_deleted_key_duplicate_prevents_database_constraint_error():
    db = AsyncMock()
    rows = MagicMock()
    rows.scalar.return_value = 123
    db.execute.return_value = rows
    with pytest.raises(BusinessException):
        await ConfigService(db).create(ConfigForm(configName="名称", configKey="deleted.key", configValue="value"))
    assert "is_deleted" not in str(db.execute.call_args.args[0]).split("WHERE")[1]
