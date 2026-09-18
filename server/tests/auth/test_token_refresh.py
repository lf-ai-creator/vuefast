"""两种令牌模式的续期与撤销回归，使用内存 Redis。"""

import pytest

from app.auth.schemas import SysUserDetails
from app.auth.token import JwtTokenManager, RedisTokenManager


class MemoryRedis:
    def __init__(self):
        self.values = {}
        self.sets = {}

    async def get(self, key):
        return self.values.get(key)

    async def setex(self, key, ttl, value):
        self.values[key] = value

    async def getdel(self, key):
        return self.values.pop(key, None)

    async def incr(self, key):
        self.values[key] = str(int(self.values.get(key, "0")) + 1)
        return int(self.values[key])

    async def sadd(self, key, value):
        self.sets.setdefault(key, set()).add(value)

    async def expire(self, key, ttl):
        pass

    async def smembers(self, key):
        return self.sets.get(key, set())

    async def delete(self, key):
        self.values.pop(key, None)
        self.sets.pop(key, None)


@pytest.fixture(params=[JwtTokenManager, RedisTokenManager])
def manager(request):
    return request.param(MemoryRedis())


@pytest.fixture
def user():
    return SysUserDetails(
        userId=10, username="member", deptId=7, roles={"MEMBER"}, dataScopes=[{"roleCode": "MEMBER", "dataScope": 3}]
    )


@pytest.mark.anyio
async def test_refresh_preserves_authorization_context(manager, user):
    token = await manager.generate_token(user)
    refreshed = await manager.refresh_token(token.refreshToken)
    assert refreshed is not None
    parsed = await manager.parse_token(refreshed.accessToken)
    assert parsed.model_dump() == user.model_dump()


@pytest.mark.anyio
async def test_revocation_blocks_access_and_refresh(manager, user):
    token = await manager.generate_token(user)
    await manager.invalidate_user_sessions(user.userId)
    assert await manager.parse_token(token.accessToken) is None
    assert await manager.refresh_token(token.refreshToken) is None


@pytest.mark.anyio
async def test_logout_blocks_refresh(manager, user):
    token = await manager.generate_token(user)
    await manager.invalidate_token(token.accessToken)
    assert await manager.refresh_token(token.refreshToken) is None
