"""认证路由。"""

from fastapi import APIRouter, Depends, Query, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CaptchaResult, LoginForm, LoginResult, RefreshTokenForm, SysUserDetails
from app.auth.service import AuthService
from app.captcha.service import CaptchaService
from app.database import get_db
from app.dependencies import get_current_user, oauth2_scheme
from app.exceptions import BusinessException
from app.rate_limit import check_rate_limit
from app.response import Result, ResultCode
from app.system.log.constants import ActionTypeEnum, LogModuleEnum
from app.system.log.operation_log import operation_log

router = APIRouter(prefix="/api/v1/auth", tags=["认证管理"])


@router.post("/login", summary="账号密码登录")
@operation_log(module=LogModuleEnum.LOGIN, action_type=ActionTypeEnum.LOGIN, title="用户登录")
async def login(request: Request, form: LoginForm, db: AsyncSession = Depends(get_db)):
    """用户名 + 密码 + 验证码登录。"""
    if not await CaptchaService().verify(form.captchaId, form.captchaCode):
        raise BusinessException(code=ResultCode.CAPTCHA_ERROR, msg="验证码错误")

    result = await AuthService(db).login(form.username, form.password)
    request.state.operation_log_user_id = result.get("userId")
    request.state.operation_log_user_name = form.username
    return Result(data=LoginResult(**result))


@router.post("/login/sms", summary="短信验证码登录")
async def login_by_sms(
    mobile: str = Query(...),
    code: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    result = await AuthService(db).login_by_sms(mobile, code)
    return Result(data=LoginResult(**result))


@router.post("/sms/code", summary="发送登录短信验证码")
async def send_sms_code(mobile: str, db: AsyncSession = Depends(get_db)):
    # 同一手机号 60 秒内仅允许发送一次验证码
    await check_rate_limit(f"rate_limit:api:sms:{mobile}", 1, 60)
    await AuthService(db).send_sms_code(mobile)
    return Result(data=None)


@router.delete("/logout", summary="登出")
async def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
    user: SysUserDetails = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if credentials is None:
        return Result(code=ResultCode.TOKEN_INVALID, msg="未提供认证令牌", data=None)
    await AuthService(db).logout(credentials.credentials)
    return Result(data=None)


@router.post("/refresh-token", summary="刷新令牌")
async def refresh_token(form: RefreshTokenForm, db: AsyncSession = Depends(get_db)):
    result = await AuthService(db).refresh_token(form.refreshToken)
    return Result(data=LoginResult(**result))


@router.get("/captcha", summary="获取验证码")
async def get_captcha():
    result = await CaptchaService().generate()
    return Result(data=CaptchaResult(captchaId=result.captchaId, captchaBase64=result.captchaBase64))
