# Youlai Admin 全栈项目

Youlai Admin 是一个前后端分离的企业级管理系统示例，当前仓库包含 PC 管理端、uni-app 移动端和 FastAPI 后端三个子工程。

## 项目结构

```text
.
├── web/       # Vue 3 + Vite + TypeScript + Element Plus，PC 管理端
├── app/       # Vue 3 + uni-app + TypeScript + Wot UI，多端移动应用
├── server/    # FastAPI + SQLAlchemy + PostgreSQL/Redis，后端 API
└── AGENTS.md  # 仓库协作与开发约定
```

各子工程依赖、脚本和配置彼此独立，请进入对应目录执行命令。根目录没有统一的构建脚本。

系统功能清单与业务边界见 [系统功能说明](docs/SYSTEM_FEATURES.md)。

## 技术栈

| 子工程   | 技术栈                                       | 默认开发地址                |
| -------- | -------------------------------------------- | --------------------------- |
| `web`    | Vue 3、Vite、TypeScript、Element Plus、Pinia | `http://localhost:3000`     |
| `app`    | Vue 3、uni-app、TypeScript、Pinia、Wot UI    | H5 `http://localhost:4096`  |
| `server` | FastAPI、SQLAlchemy Async、PostgreSQL、Redis | API `http://127.0.0.1:8000` |

## 快速开始

### 1. 启动后端

后端需要 Python 3.11+、PostgreSQL 和 Redis。复制配置并填写本地连接信息：

```bash
cd server
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/macOS
python -m pip install -e ".[dev]"
```

初始化数据库可使用 `server/sql/postgresql/youlai-admin.sql`，然后启动：

```bash
python -m uvicorn app.main:app --reload
```

也可在 Windows 使用 `./start-server.ps1`，停止使用 `./stop-server.ps1`。接口文档：`http://127.0.0.1:8000/docs`。

### 2. 启动 PC 管理端

```bash
cd web
pnpm install
pnpm dev
```

开发环境默认通过 `web/.env.development` 将 `/dev-api` 代理到 `http://127.0.0.1:8000`。如需独立开发，可将 `VITE_MOCK_DEV_SERVER=true` 启用 Mock。

### 3. 启动移动端

```bash
cd app
pnpm install
pnpm dev:h5
```

微信小程序：

```bash
pnpm dev:mp-weixin
```

移动端 API 地址和端口由 `app/.env.development` 控制；生产构建使用 `pnpm build:h5` 或对应平台的 `build:*` 脚本。

默认演示账号通常为 `admin / 123456`，实际是否可用取决于数据库初始化数据。

## 常用验证命令

```bash
# web/
pnpm type-check
pnpm build
pnpm lint

# app/
pnpm type-check
pnpm check
pnpm build:h5

# server/
pytest
ruff check .
ruff format .
```

## 配置与安全

- `server/.env` 只保存本地真实配置，已被忽略，禁止提交凭据。
- 使用 `server/.env.example` 作为脱敏模板，并为 `JWT_SECRET_KEY` 生成至少 32 字符的随机值。
- 前端 `.env.*` 会进入构建产物，只放公开地址和开关，不放后端密钥。
- 短信、邮件等外部服务未配置时，相关接口会明确返回未接入提示。

## 目录约定

- `web/src/views`、`web/src/components`、`web/src/api`：PC 页面、公共组件和接口封装。
- `app/src/pages`、`app/src/subPages`、`app/src/components`、`app/src/api`：移动端页面、分包页面、组件和接口。
- `server/app`、`server/alembic`、`server/sql`、`server/tests`：后端业务、迁移、SQL 和测试。

## 许可证

本项目整体采用 [MIT License](LICENSE) 开源协议。`web/` 和 `app/` 子工程已包含对应 MIT 许可证文件；后端 `server/` 与根项目保持一致。
