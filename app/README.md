<div align="center">

# <img alt="youlai-app" height="32" valign="middle" src="./public/logo.png"> youlai-app

**基于 uni-app、Vue 3、TypeScript 和 Wot UI 的移动端跨平台应用模板**

[![Vue](https://img.shields.io/badge/Vue-3.5-42b883?logo=vue.js)](https://vuejs.org/)
[![uni-app](https://img.shields.io/badge/uni--app-3.x-2b9939)](https://uniapp.dcloud.net.cn/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178c6?logo=typescript)](https://www.typescriptlang.org/)
[![Wot UI](https://img.shields.io/badge/Wot%20UI-2.x-4f8cff)](https://wot-ui.cn/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](LICENSE)

[在线预览](https://app.youlai.tech) | [项目文档](https://www.youlai.tech/docs/app/) | [配套后端](https://www.youlai.tech/docs/server/) | [PC 管理端](https://www.youlai.tech/docs/web/)

</div>

## 项目介绍

**youlai-app** 是有来开源生态的移动端项目，面向 H5、微信小程序和 App 等多端场景，适合用作企业中后台、会员中心、移动工作台、小程序业务端的二次开发基础。

项目和 [vue3-element-admin](https://gitee.com/youlaiorg/vue3-element-admin)、[youlai-boot](https://gitee.com/youlaiorg/youlai-boot) 使用同一套接口规范，可直接对接 Java / Node.js / Go / Python / PHP / C# 等多种后端实现。

## 核心特性

- **跨端开发**：一套代码支持 H5、微信小程序、App 等平台。
- **Vue 3 技术栈**：基于 Vue 3、TypeScript、Pinia、Vite 和 uni-app。
- **Wot UI 组件库**：移动端组件风格统一，适合快速搭建业务页面。
- **自动化能力**：集成页面路由、组件自动导入、API 自动导入等常用工程能力。
- **规范化工程**：内置 ESLint、Prettier、Stylelint、Husky、Commitlint。
- **生态联动**：可与 `vue3-element-admin` 和有来多语言后端无缝配套使用。

## 系统预览

<table align="center">
  <tr>
    <td><img alt="APP 预览 1" width="200" src="./public/images/preview/app-01.png"></td>
    <td><img alt="APP 预览 2" width="200" src="./public/images/preview/app-02.png"></td>
    <td><img alt="APP 预览 3" width="200" src="./public/images/preview/app-03.png"></td>
    <td><img alt="APP 预览 4" width="200" src="./public/images/preview/app-04.png"></td>
  </tr>
</table>

## 在线体验

| 类型 | 地址 |
|:-----|:-----|
| H5 预览 | [https://app.youlai.tech](https://app.youlai.tech) |
| 官方文档 | [https://www.youlai.tech/docs/app/](https://www.youlai.tech/docs/app/) |
| PC 管理端 | [https://vue.youlai.tech](https://vue.youlai.tech) |
| Apifox 接口文档 | [https://www.apifox.cn/apidoc/shared-195e783f-4d85-4235-a038-eec696de4ea5](https://www.apifox.cn/apidoc/shared-195e783f-4d85-4235-a038-eec696de4ea5) |

默认账号：`admin` / `123456`

## 快速开始

### 环境要求

- Node.js 18+
- pnpm 8+
- 微信开发者工具（运行微信小程序时需要）

### 安装依赖

```bash
pnpm install
```

> **提示**：`src/pages.json` 是构建产物（由 `pages.config.json` 与各页面的 `definePage` 宏生成），不随仓库提交。克隆项目后如需使用 HBuilderX 等依赖该文件的工具，请先运行一次任意构建或启动命令（如 `pnpm run dev:h5`）生成。请勿手工编辑该文件：页面路由请修改对应页面的 `definePage`，全局配置（tabBar、globalStyle 等）请修改根目录 `pages.config.json`。

### H5 启动

```bash
pnpm run dev:h5
```

启动后访问 [http://localhost:4096](http://localhost:4096)。

### H5 打包

```bash
pnpm run build:h5
```

构建产物默认输出到 `dist/build/h5`，可部署到 Nginx、OSS、静态站点托管等服务。

## 微信小程序

### 开发调试

```bash
pnpm run dev:mp-weixin
```

编译完成后，使用微信开发者工具导入 `dist/dev/mp-weixin` 目录。

### 生产打包

```bash
pnpm run build:mp-weixin
```

构建产物默认输出到 `dist/build/mp-weixin`，在微信开发者工具中导入后即可预览、上传和提交审核。

### 微信开发者工具配置

导入项目后，进入右上角 **详情** → **本地设置**，建议开发环境按以下方式配置：

- 勾选 **不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书**。
- 勾选 **ES6 转 ES5**。
- 取消勾选 **过滤无依赖文件**，避免部分组件无法加载。
- 如遇组件加载异常，可依次尝试清除缓存、重新编译、重新载入项目配置。

## 常用命令

| 命令 | 说明 |
|:-----|:-----|
| `pnpm run dev:h5` | 启动 H5 开发服务 |
| `pnpm run build:h5` | 构建 H5 生产包 |
| `pnpm run dev:mp-weixin` | 编译微信小程序开发包 |
| `pnpm run build:mp-weixin` | 构建微信小程序生产包 |
| `pnpm run dev:app` | 启动 App 开发编译 |
| `pnpm run build:app` | 构建 App 生产包 |
| `pnpm run type-check` | TypeScript 类型检查 |
| `pnpm run lint:eslint` | ESLint 检查并修复 |
| `pnpm run lint:prettier` | Prettier 格式化 |
| `pnpm run lint:stylelint` | Stylelint 检查并修复 |

## 目录结构

```text
youlai-app/
├── docs/                         # README 预览图、二维码等文档资源
├── public/                       # 静态资源
├── src/
│   ├── api/                      # 接口请求
│   ├── components/               # 通用组件和业务组件
│   ├── composables/              # 组合式函数
│   ├── config/                   # 项目配置
│   ├── constants/                # 常量定义
│   ├── enums/                    # 枚举定义
│   ├── layouts/                  # 页面布局
│   ├── pages/                    # 页面文件
│   ├── router/                   # 路由配置
│   ├── static/                   # 应用静态资源
│   ├── store/                    # Pinia 状态管理
│   ├── styles/                   # 全局样式
│   ├── types/                    # 类型声明
│   ├── utils/                    # 工具函数
│   ├── App.vue                   # 应用入口组件
│   ├── main.ts                   # 应用入口文件
│   ├── manifest.json             # uni-app 应用配置
│   └── pages.json                # 页面和导航配置
├── package.json                  # 依赖和脚本
├── pages.config.ts               # 页面生成配置
├── unocss.config.ts              # UnoCSS 配置
└── vite.config.ts                # Vite 配置
```

## 配套生态

| 项目 | 技术栈 | 说明 |
|:-----|:-------|:-----|
| [vue3-element-admin](https://gitee.com/youlaiorg/vue3-element-admin) | Vue 3 + Element Plus | PC 管理端 |
| [youlai-boot](https://gitee.com/youlaiorg/youlai-boot) | Spring Boot | Java 后端 |
| [youlai-nest](https://gitee.com/youlaiorg/youlai-nest) | NestJS + TypeORM | Node.js 后端 |
| [youlai-gin](https://gitee.com/youlaiorg/youlai-gin) | Go + Gorm | Go 后端 |
| [youlai-django](https://gitee.com/youlaiorg/youlai-django) | Django + DRF | Python 后端 |
| [youlai-think](https://gitee.com/youlaiorg/youlai-think) | ThinkPHP 8 | PHP 后端 |
| [youlai-aspnet](https://gitee.com/youlaiorg/youlai-aspnet) | ASP.NET Core | C# 后端 |

## 技术合作

本项目采用 [Apache License 2.0](LICENSE) 开源，可免费商用。欢迎在 [Issue](https://gitee.com/youlaiorg/youlai-app/issues) 提交问题或反馈，也欢迎提交 [Pull Request](https://gitee.com/youlaiorg/youlai-app/pulls) 共建。

如需技术支持、商务合作、二次开发、项目定制或私有化部署，可联系作者微信（见下方二维码）。

<table align="center">
  <tr>
    <td align="center">
      <img src="./public/images/qrcode/wechat-official.jpg" height="180" alt="公众号「有来技术」"><br>
      <sub>公众号「有来技术」</sub>
    </td>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
    <td align="center">
      <img src="./public/images/qrcode/wechat-mp.jpg" height="180" alt="小程序「有来技术」"><br>
      <sub>小程序「有来技术」</sub>
    </td>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
    <td align="center">
      <img src="./public/images/qrcode/wechat-personal.png" height="180" alt="添加作者微信"><br>
      <sub>添加作者微信</sub>
    </td>
  </tr>
</table>

<p align="center"><em>技术交流 · 问题反馈 · 商务合作</em></p>
