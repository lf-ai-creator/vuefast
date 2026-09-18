"""图形验证码服务 — Pillow 生成 + Redis 存储。"""

import asyncio
import base64
import io
import string
import uuid
from secrets import SystemRandom, choice

from loguru import logger
from PIL import Image, ImageDraw, ImageFont

from app.auth.schemas import CaptchaResult
from app.captcha.constants import CAPTCHA_TTL
from app.constants import REDIS_CAPTCHA_PREFIX
from app.redis import get_redis

_IMAGE_RANDOM = SystemRandom()


class CaptchaService:
    """图形验证码服务。"""

    @staticmethod
    def _random_code(length: int = 4) -> str:
        """生成随机字母数字验证码。"""
        chars = string.ascii_letters + string.digits
        # 排除易混淆字符
        chars = chars.translate(str.maketrans("", "", "0OIl1"))
        return "".join((choice(chars) for _ in range(length)))

    @staticmethod
    def _generate_image(code: str, width: int = 130, height: int = 50) -> bytes:
        """Pillow 生成带干扰的验证码图片。"""
        img = Image.new("RGB", (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)

        # 验证码文字
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except OSError:
            font = ImageFont.load_default()

        for i, char in enumerate(code):
            x = 15 + i * 28 + _IMAGE_RANDOM.randint(-3, 3)
            y = _IMAGE_RANDOM.randint(5, 15)
            r, g, b = _IMAGE_RANDOM.randint(0, 100), _IMAGE_RANDOM.randint(0, 100), _IMAGE_RANDOM.randint(0, 100)
            draw.text((x, y), char, font=font, fill=(r, g, b))

        # 干扰线
        for _ in range(5):
            x1, y1 = _IMAGE_RANDOM.randint(0, width), _IMAGE_RANDOM.randint(0, height)
            x2, y2 = _IMAGE_RANDOM.randint(0, width), _IMAGE_RANDOM.randint(0, height)
            draw.line((x1, y1, x2, y2), fill=(180, 180, 180), width=1)

        # 干扰点
        for _ in range(50):
            x, y = _IMAGE_RANDOM.randint(0, width), _IMAGE_RANDOM.randint(0, height)
            draw.point((x, y), fill=(180, 180, 180))

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    async def generate(self) -> CaptchaResult:
        """生成验证码并存入 Redis。"""
        code = self._random_code(4)
        captcha_id = uuid.uuid4().hex

        redis_client = await get_redis()
        await redis_client.setex(
            f"{REDIS_CAPTCHA_PREFIX}{captcha_id}",
            CAPTCHA_TTL,
            code.lower(),
        )

        # Pillow 图片生成放入线程池避免阻塞事件循环
        loop = asyncio.get_running_loop()
        img_bytes = await loop.run_in_executor(None, self._generate_image, code)
        img_base64 = base64.b64encode(img_bytes).decode()

        logger.info(f"Captcha generated: id={captcha_id}")
        return CaptchaResult(captchaId=captcha_id, captchaBase64=f"data:image/png;base64,{img_base64}")

    async def verify(self, captcha_id: str, code: str) -> bool:
        """校验验证码 — 一次性使用。"""
        redis_client = await get_redis()
        key = f"{REDIS_CAPTCHA_PREFIX}{captcha_id}"
        stored = await redis_client.getdel(key)
        return stored is not None and stored == code.lower()
