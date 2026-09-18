"""全局中间件。"""

import time

from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.exceptions import BusinessException
from app.rate_limit import check_rate_limit


def setup_cors(app):
    origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials="*" not in origins,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Client-Platform",
            "X-Client-Platform-Version",
        ],
        expose_headers=["Content-Disposition"],
        max_age=600,
    )


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")
        return response


class IpRateLimitMiddleware(BaseHTTPMiddleware):
    """IP 全局滑动窗口限流（ZSet Lua 原子计数），Redis 异常时放行。"""

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or request.headers.get("x-real-ip", "").strip()
            or (request.client.host if request.client else "unknown")
        )
        key = f"rate_limit:ip:{client_ip}"
        limit = settings.RATE_LIMIT_IP_LIMIT
        window = settings.RATE_LIMIT_IP_WINDOW
        try:
            count = await check_rate_limit(key, limit, window)
        except BusinessException as e:
            response = JSONResponse(
                status_code=e.http_status,
                content={"code": e.code, "msg": e.msg, "data": None},
            )
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
            response.headers["Retry-After"] = str(window)
            return response

        response = await call_next(request)
        remaining = max(0, limit - (count or 0))
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
        return response
