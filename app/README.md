# App 移动端

`app` 是 Youlai Admin 的 uni-app 客户端，使用 Vue 3、TypeScript、Pinia、Vite 和 Wot UI，支持 H5、微信小程序以及 uni-app 支持的 App/小程序平台。

## 环境要求

- Node.js 18+
- pnpm 8+
- 运行微信小程序需要微信开发者工具

## 安装与运行

```bash
pnpm install
pnpm dev:h5              # H5，默认 http://localhost:4096
pnpm build:h5            # H5 生产包
pnpm dev:mp-weixin       # 微信小程序开发包
pnpm build:mp-weixin     # 微信小程序生产包
```

其他平台使用 `package.json` 中对应的 `dev:*` / `build:*` 脚本，例如 `dev:app`、`build:app-android`、`build:mp-alipay`。微信小程序编译结果位于 `dist/dev/mp-weixin` 或 `dist/build/mp-weixin`。

## 环境变量

开发配置位于 `.env.development`，生产配置位于 `.env.production`：

| 变量                | 作用               | 开发默认值                |
| ------------------- | ------------------ | ------------------------- |
| `VITE_APP_PORT`     | H5 开发端口        | `4096`                    |
| `VITE_APP_BASE_API` | H5 代理前缀        | `/dev-api`                |
| `VITE_APP_API_URL`  | API 地址或代理目标 | `https://api.youlai.tech` |

本地联调 FastAPI 时，可将 `VITE_APP_API_URL` 改为 `http://127.0.0.1:8000`。公开构建中只能放公开配置，不能放密钥。

## 页面路由说明

页面位于 `src/pages`，分包页面位于 `src/subPages`，路由由 `pages.config.ts` 和页面配置生成。不要手工维护构建生成的 `src/pages.json`（如构建工具生成该文件）。

## 目录结构

```text
src/
├── api/          # 接口封装
├── components/   # 公共组件
├── composables/  # 组合式逻辑
├── config/       # 菜单和运行配置
├── layouts/      # 页面布局
├── pages/        # 主包页面
├── subPages/     # 分包页面
├── router/       # uni-mini-router 路由
├── store/        # Pinia 状态
├── static/       # 静态资源
└── utils/        # 工具函数
```

## 检查命令

```bash
pnpm type-check
pnpm check
pnpm lint:prettier
```

## 相关工程

- PC 管理端：[`../web`](../web)
- FastAPI 后端：[`../server`](../server)
- 全局说明：[`../README.md`](../README.md)
