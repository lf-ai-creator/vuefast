"""日志统计日期类型、统计范围及总数回归测试。"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.system.log.router import LogService


@pytest.mark.asyncio
async def test_trend_uses_typed_dates_and_fills_empty_days():
    db = AsyncMock()
    db.execute.side_effect = [[(date(2026, 9, 19), 4)], [(date(2026, 9, 19), 2)]]
    result = await LogService(db).get_visit_trend(date(2026, 9, 13), date(2026, 9, 19))
    assert len(result.dates) == 7
    assert result.pvList == [0, 0, 0, 0, 0, 0, 4]
    assert result.uvList == [0, 0, 0, 0, 0, 0, 2]
    for call in db.execute.call_args_list:
        statement = call.args[0]
        assert set(statement.compile().params.values()) == {
            datetime(2026, 9, 13), datetime(2026, 9, 20)
        }
        assert "sys_log.create_time < " in str(statement)


@pytest.mark.asyncio
async def test_reversed_range_is_validation_error():
    db = AsyncMock()
    with pytest.raises(HTTPException) as error:
        await LogService(db).get_visit_trend(date(2026, 9, 19), date(2026, 9, 13))
    assert error.value.status_code == 422
    db.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_overview_uses_date_parameters_and_counts_log_table():
    db = AsyncMock()
    results = []
    for count in [3, 2, 5, 6, 4, 10]:
        row = MagicMock()
        row.scalar.return_value = count
        results.append(row)
    db.execute.side_effect = results
    result = await LogService(db).get_visit_overview()
    assert result.totalPvCount == 10
    assert result.uvGrowthRate == 50
    assert result.pvGrowthRate == 50
    for index in (0, 1, 3, 4):
        params = db.execute.call_args_list[index].args[0].compile().params
        assert all(isinstance(value, date) for value in params.values())
    assert "FROM sys_log" in str(db.execute.call_args_list[-1].args[0])
