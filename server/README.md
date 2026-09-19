# FastAPI 后端

`server` 是 Youlai Admin 的 API 服务，基于 FastAPI、SQLAlchemy Async、PostgreSQL 和 Redis，提供认证、权限、系统管理、日志、文件、代码生成、SSE 等模块。

## 环境要求

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- 可选：S3/RustFS，用于对象存储和文件上传

## 安装与配置

```bash
cd server
python -m venv .venv
.venv\Scripts\activate              # Windows
# source .venv/bin/activate           # Linux/macOS
python -m pip install -e ".[dev]"
copy .env.example .env               # Windows
# cp .env.example .env                # Linux/macOS
```

编辑 `.env`，至少配置 `DATABASE_URL`、`REDIS_URL` 和长度不少于 32 位的随机 `JWT_SECRET_KEY`。`.env` 只用于本地，不要提交。

## 数据库

首次部署可执行初始化 SQL：

```bash
psql "$DATABASE_URL" -f sql/postgresql/youlai-admin.sql
```

后续结构变更使用 Alembic：

```bash
alembic upgrade head
```

也可使用 Docker Compose 启动 API、PostgreSQL、Redis 和 RustFS：

```bash
docker compose up -d --build
```

Compose 中的密钥只适合本地开发，生产环境必须替换。

## 启动与接口文档

```bash
python -m uvicorn app.main:app --reload
```

服务默认监听 `http://127.0.0.1:8000`，文档地址：

- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`

Windows 可使用 `start-server.ps1` 和 `stop-server.ps1` 管理服务。启动脚本会将运行状态和日志写入 `.runtime/`。

## 主要模块

```text
app/
├── auth/       # 登录、登出、刷新令牌、验证码
├── system/     # 用户、角色、菜单、部门、字典、配置、通知、日志
├── tool/       # 文件、代码生成、SSE、微信小程序
├── captcha/    # 图片验证码
├── database.py # 异步数据库连接
├── redis.py    # Redis 连接
├── config.py   # Pydantic Settings 配置
└── main.py     # FastAPI 应用入口
alembic/        # 数据库迁移
sql/            # 初始化 SQL
tests/          # pytest 测试
```

## 配置项

完整脱敏模板见 [`.env.example`](.env.example)。主要配置包括：

| 配置               | 说明                       |
| ------------------ | -------------------------- |
| `DATABASE_URL`     | PostgreSQL 异步连接串      |
| `REDIS_URL`        | Redis 连接串               |
| `JWT_SECRET_KEY`   | JWT 签名密钥，至少 32 字符 |
| `S3_*`             | RustFS/S3 文件存储配置     |
| `MAIL_*`           | 邮件服务配置               |
| `ALLOWED_ORIGINS`  | CORS 来源列表，逗号分隔    |
| `FILE_MAX_SIZE_MB` | 文件上传大小限制           |

短信和邮件验证码接口在未配置外部服务时会返回未接入提示，不应在生产环境中伪造验证码。

## 测试与质量检查

```bash
pytest
ruff check .
ruff format .
```

## 相关工程

- PC 管理端：[`../web`](../web)
- 移动端：[`../app`](../app)
- 全局说明：[`../README.md`](../README.md)
