# Web 管理端

`web` 是 Youlai Admin 的 PC 管理后台，基于 Vue 3、Vite、TypeScript、Element Plus、Pinia 和 Vue Router 构建。

## 环境要求

- Node.js `^20.19.0` 或 `>=22.12.0`
- pnpm `>=8`

## 启动与构建

```bash
pnpm install
pnpm dev              # http://localhost:3000
pnpm build            # 类型检查并构建 dist
pnpm preview          # 预览 dist
```

Windows 也可以使用 `start-web.ps1` / `stop-web.ps1` 管理开发服务。

## 环境变量

开发配置位于 `.env.development`：

| 变量                      | 作用              | 当前默认值              |
| ------------------------- | ----------------- | ----------------------- |
| `VITE_APP_PORT`           | Vite 开发端口     | `3000`                  |
| `VITE_APP_BASE_API`       | 浏览器请求前缀    | `/dev-api`              |
| `VITE_APP_API_URL`        | API 代理目标      | `http://127.0.0.1:8000` |
| `VITE_MOCK_DEV_SERVER`    | 是否启用本地 Mock | `false`                 |
| `VITE_APP_TENANT_ENABLED` | 是否启用多租户 UI | `false`                 |

生产配置位于 `.env.production`，默认使用 `/prod-api` 前缀。环境变量会进入公开前端构建产物，不要放置密钥。

## 目录结构

```text
src/
├── api/          # API 请求与类型
├── assets/       # 源码资源
├── components/   # 公共组件
├── composables/  # 组合式逻辑
├── layouts/      # 布局与导航
├── router/       # 路由与权限守卫
├── stores/       # Pinia 状态
├── styles/       # 全局样式与 Element Plus 覆盖
└── views/        # 业务页面
mock/             # Mock 接口
public/           # 原样复制的静态资源
```

## 校验命令

```bash
pnpm type-check
pnpm lint:eslint
pnpm lint:stylelint
pnpm lint
```

`lint` 会执行自动修复，请提交前确认变更范围。接口默认通过 `/dev-api` 代理到 `server`，也可以将 `VITE_MOCK_DEV_SERVER` 设为 `true` 独立开发。

## 相关工程

- 移动端：[`../app`](../app)
- FastAPI 后端：[`../server`](../server)
- 全局说明：[`../README.md`](../README.md)

## 许可证

本子工程采用 [MIT License](LICENSE)。

## 来源与致谢

本子工程来源于 [youlaiorg/vue3-element-admin](https://gitee.com/youlaiorg/vue3-element-admin)，在原项目基础上进行仓库整合、功能调整和界面优化。感谢原项目作者及所有贡献者。
