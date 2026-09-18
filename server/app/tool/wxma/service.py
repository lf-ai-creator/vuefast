"""微信认证服务：接入服务端身份验证前禁止登录和绑定。"""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


class WxMaAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def silent_login(self, code: str) -> dict:
        raise HTTPException(status_code=501, detail="微信登录尚未接入，请使用账号密码登录")

    async def phone_login(self, form) -> dict:
        raise HTTPException(status_code=501, detail="微信手机号授权尚未接入")

    async def bind_mobile(self, form) -> dict:
        raise HTTPException(status_code=501, detail="微信手机号绑定尚未接入")
