"""共享接口参数校验。"""

from app.exceptions import BusinessException
from app.response import ResultCode


def parse_ids(value: str) -> list[int]:
    """解析批量 ID，避免无效参数进入数据库并触发 500。"""
    try:
        ids = list(dict.fromkeys(int(part.strip()) for part in value.split(",")))
    except ValueError as error:
        raise BusinessException(code=ResultCode.PARAM_VALID_FAIL, msg="ID 必须是逗号分隔的正整数") from error
    if not ids or len(ids) > 1000 or any(item <= 0 or item > 2**63 - 1 for item in ids):
        raise BusinessException(code=ResultCode.PARAM_VALID_FAIL, msg="ID 列表无效或超过 1000 条")
    return ids
