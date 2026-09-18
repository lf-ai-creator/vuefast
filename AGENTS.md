# Repository Guidelines

## 项目结构与模块划分

- `web/`：Vue 3、TypeScript、Vite 和 Element Plus 管理后台。页面、公共组件和接口封装分别位于 `src/views/`、`src/components/` 和 `src/api/`；资源位于 `src/assets/` 和 `public/`，模拟接口位于 `mock/`。
- `app/`：Vue 3/TypeScript uni-app 客户端。页面位于 `src/pages/` 和 `src/subPages/`；公共组件、接口封装和静态资源分别位于 `src/components/`、`src/api/` 和 `src/static/`。
- `server/`：FastAPI 后端。业务模块位于 `app/auth/`、`app/system/` 和 `app/tool/`；迁移、SQL、文档和测试分别位于 `alembic/`、`sql/`、`docs/` 和 `tests/`。

## 构建、测试与本地开发

在对应模块目录执行命令；根目录没有统一构建脚本。

- 两个客户端：`pnpm install` 安装依赖；`pnpm type-check` 检查 Vue/TypeScript 类型。
- `web/`：`pnpm dev` 启动开发服务；`pnpm build` 检查类型并构建生产资源；`pnpm lint` 执行 ESLint、Prettier 和 Stylelint，并自动修复文件。
- `app/`：`pnpm dev:h5` 启动 H5 开发服务；`pnpm build:h5` 构建生产资源；`pnpm check` 检查类型和代码规范；`pnpm dev:mp-weixin` 用于微信小程序开发。
- `server/`：`python -m pip install -e ".[dev]"` 安装后端及开发依赖；`uvicorn app.main:app --reload` 启动 API；`pytest` 执行测试；`ruff check .` 检查 Python 代码，`ruff format .` 格式化代码。

## 代码风格与命名

客户端使用两空格缩进、双引号和分号，遵循各模块的 Prettier 配置。组件和目录命名沿用相邻代码的约定；共享逻辑放入 composables，接口调用放入 API 模块。

Python 使用四空格缩进，函数和模块使用 `snake_case`，类使用 `PascalCase`。Ruff 目标版本为 Python 3.11，行宽上限为 120 字符。路由和业务逻辑放入对应业务模块。

## 测试规范

后端使用 pytest、pytest-asyncio 和 HTTPX，公共测试夹具位于 `tests/conftest.py`。测试文件命名为 `test_*.py`，测试函数命名为 `test_*`；修改后端行为时补充回归测试。`pytest` 输出未覆盖代码并生成 HTML 覆盖率报告，目前未配置最低覆盖率要求。

两个客户端均未配置自动化测试脚本。提交前执行类型检查、代码规范检查和对应构建，并手动验证受影响的页面及目标平台。

## 提交与拉取请求

当前检出目录没有可用的 Git 历史。客户端 Commitlint 配置采用 Conventional Commits，例如 `fix(auth): 修复令牌过期处理`。每次提交聚焦一个明确改动。

拉取请求应说明行为变化、关联相关问题并列出验证结果；界面变化附截图，配置或数据库迁移变化说明操作要求。

## 安全与配置

禁止提交凭据。执行后端集成验证前配置 PostgreSQL 和 Redis。客户端环境变量会进入公开构建产物，不得存放后端密钥。
