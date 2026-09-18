<template>
  <view class="about">
    <wd-card>
      <view class="about__header">
        <image class="about__logo" src="/static/images/logo.png" mode="aspectFit" />
        <view class="about__info">
          <text class="about__app-title">youlai-app</text>
          <text class="about__app-version">版本 {{ version }}</text>
        </view>
      </view>

      <view class="about__intro">
        <text class="about__intro-title">项目介绍</text>
        <text class="about__intro-desc">
          一个基于 uni-app + Vue 3 + TypeScript 的移动端模板，内置主题系统与 wot-design-uni
          组件库。同时提供管理端与多后端版本（Java / Gin / Nest / Django / ThinkPHP /
          ASP.NET），并包含多租户实现。
        </text>
      </view>
    </wd-card>

    <wd-card title="仓库" class="mt-20rpx">
      <wd-collapse v-model="collapseActive" accordion>
        <wd-collapse-item title="Web 前端" name="web">
          <wd-cell-group border>
            <wd-cell
              title="vue3-element-admin"
              icon="desktop"
              clickable
              is-link
              @click="openProjectIntro('vue3-element-admin')"
            />
            <wd-cell
              title="vue3-element-admin-js"
              icon="desktop"
              clickable
              is-link
              @click="openProjectIntro('vue3-element-admin-js')"
            />
            <wd-cell
              title="vue3-element-template"
              icon="desktop"
              clickable
              is-link
              @click="openProjectIntro('vue3-element-template')"
            />
          </wd-cell-group>
        </wd-collapse-item>

        <wd-collapse-item title="移动端" name="mobile">
          <wd-cell-group border>
            <wd-cell
              title="youlai-app"
              icon="mobile"
              clickable
              is-link
              @click="openProjectIntro('youlai-app')"
            />
          </wd-cell-group>
        </wd-collapse-item>

        <wd-collapse-item title="后端（6 种技术栈）" name="backend">
          <wd-cell-group border>
            <wd-cell
              title="youlai-boot"
              icon="cloud"
              clickable
              is-link
              @click="openProjectIntro('youlai-boot')"
            />
            <wd-cell
              title="youlai-gin"
              icon="cloud"
              clickable
              is-link
              @click="openProjectIntro('youlai-gin')"
            />
            <wd-cell
              title="youlai-nest"
              icon="cloud"
              clickable
              is-link
              @click="openProjectIntro('youlai-nest')"
            />
            <wd-cell
              title="youlai-django"
              icon="cloud"
              clickable
              is-link
              @click="openProjectIntro('youlai-django')"
            />
            <wd-cell
              title="youlai-think"
              icon="cloud"
              clickable
              is-link
              @click="openProjectIntro('youlai-think')"
            />
            <wd-cell
              title="youlai-aspnet"
              icon="cloud"
              clickable
              is-link
              @click="openProjectIntro('youlai-aspnet')"
            />
          </wd-cell-group>
        </wd-collapse-item>

        <wd-collapse-item title="多租户" name="tenant">
          <wd-cell-group border>
            <wd-cell
              title="youlai-boot-tenant"
              icon="cloud"
              clickable
              is-link
              @click="openProjectIntro('youlai-boot-tenant')"
            />
          </wd-cell-group>
        </wd-collapse-item>
      </wd-collapse>
    </wd-card>

    <wd-card title="联系我们" class="mt-20rpx">
      <wd-cell-group border>
        <wd-cell
          title="官方网站"
          value="www.youlai.tech"
          icon="link"
          clickable
          @click="openUrl('https://www.youlai.tech')"
        />
        <wd-cell
          title="GitHub"
          value="github.com/youlaitech"
          icon="link"
          clickable
          @click="openUrl('https://github.com/youlaitech')"
        />
        <wd-cell
          title="联系邮箱"
          value="youlaitech@163.com"
          icon="email"
          clickable
          @click="copyText('youlaitech@163.com')"
        />
      </wd-cell-group>
    </wd-card>

    <view class="about__footer">
      <text class="about__copyright">Copyright {{ getYear() }} 有来开源组织</text>
      <text class="about__copyright about__copyright--sub">All Rights Reserved</text>
    </view>

    <wd-popup v-model="introPopupVisible" position="bottom">
      <view class="about__popup">
        <view class="about__popup-title">{{ currentProject?.title }}</view>
        <view v-if="currentProject?.stack" class="about__popup-stack">
          技术栈：{{ currentProject.stack }}
        </view>
        <view v-if="currentProject?.summary" class="about__popup-summary">
          {{ currentProject.summary }}
        </view>
        <view class="about__popup-action">
          <wd-button block @click="goCurrentProjectRepo">去仓库</wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script lang="ts" setup>
definePage({
  name: "about",
  style: { navigationBarTitleText: "关于系统" },
});

const version = ref(import.meta.env.VITE_APP_VERSION);
const collapseActive = ref<string[]>(["web"]);

type ProjectIntroKey =
  | "vue3-element-admin"
  | "vue3-element-admin-js"
  | "vue3-element-template"
  | "youlai-app"
  | "youlai-boot"
  | "youlai-gin"
  | "youlai-nest"
  | "youlai-django"
  | "youlai-think"
  | "youlai-aspnet"
  | "youlai-boot-tenant";

type ProjectIntroItem = {
  title: string;
  stack: string;
  summary: string;
  repoUrl: string;
};

const projectIntros: Record<ProjectIntroKey, ProjectIntroItem> = {
  "vue3-element-admin": {
    title: "vue3-element-admin",
    stack: "Vue 3.5 + Vite 7 + TypeScript + Element Plus",
    summary:
      "极简开箱即用的企业级后台管理模板，内置用户/角色/菜单/部门等基础模块，支持动态路由与按钮/数据权限，并提供暗黑模式、国际化与代码生成等能力。",
    repoUrl: "https://github.com/youlaitech/vue3-element-admin",
  },
  "vue3-element-admin-js": {
    title: "vue3-element-admin-js",
    stack: "Vue 3.5 + Vite 6 + JavaScript + Element Plus",
    summary:
      "vue3-element-admin 的 JavaScript 版本，保留核心后台能力与权限体系，适合更轻量的快速开发场景，并支持 Mock 与线上接口文档联调。",
    repoUrl: "https://github.com/youlaitech/vue3-element-admin-js",
  },
  "vue3-element-template": {
    title: "vue3-element-template",
    stack: "Vue 3.5 + Vite 6 + TypeScript 5 + Element Plus + Pinia",
    summary:
      "从 vue3-element-admin 抽离出的精简中后台模板，预置工程化规范与常用业务基座，专注高频功能与更低的二次开发成本。",
    repoUrl: "https://github.com/youlaitech/vue3-element-template",
  },
  "youlai-app": {
    title: "youlai-app",
    stack: "uni-app + Vue 3 + TypeScript + UnoCSS + wot-design-uni",
    summary:
      "跨平台移动端模板，内置代码规范与工程化工具链，适配 H5 与微信小程序等多端场景，并提供可复用的基础/业务组件体系。",
    repoUrl: "https://github.com/youlaitech/youlai-app",
  },
  "youlai-boot": {
    title: "youlai-boot",
    stack: "JDK 17 + Spring Boot 4 + Spring Security + JWT + Redis + MySQL",
    summary:
      "配套 vue3-element-admin 的 Java 后端实现，提供 RBAC 权限体系与用户/角色/菜单等核心模块，支持令牌续期与多端会话治理，并内置代码生成能力。",
    repoUrl: "https://github.com/youlaitech/youlai-boot",
  },
  "youlai-gin": {
    title: "youlai-gin",
    stack: "Go 1.21+ + Gin + GORM + JWT + Redis + MySQL",
    summary:
      "配套 vue3-element-admin 的 Go/Gin 后端实现，轻量高性能，提供 RBAC 权限模型与常用系统模块，支持 JWT 与 Redis 会话管理。",
    repoUrl: "https://github.com/youlaitech/youlai-gin",
  },
  "youlai-nest": {
    title: "youlai-nest",
    stack: "Node.js 20+ + NestJS 11 + TypeScript + TypeORM + JWT + Redis + MySQL",
    summary:
      "配套 vue3-element-admin 的 Node.js 后端实现，基于 NestJS 的企业级架构，支持 JWT 与 Redis Token 两种会话模式，并提供完整的 RBAC 权限与核心系统模块。",
    repoUrl: "https://github.com/youlaitech/youlai-nest",
  },
  "youlai-django": {
    title: "youlai-django",
    stack: "Python 3.12+ + Django 6 + DRF + SimpleJWT + Redis + MySQL",
    summary:
      "配套 vue3-element-admin 的 Python 后端实现，基于 DRF 构建，提供 RBAC 权限模型与核心系统模块，采用 JWT 认证并结合 Redis 管理会话。",
    repoUrl: "https://github.com/youlaitech/youlai-django",
  },
  "youlai-think": {
    title: "youlai-think",
    stack: "PHP 8 + ThinkPHP 8 + JWT + Redis + MySQL",
    summary:
      "配套 vue3-element-admin 的 PHP 后端实现，上手成本低，提供 RBAC 权限体系与常用系统模块，支持 JWT 与 Redis 会话双模式。",
    repoUrl: "https://github.com/youlaitech/youlai-think",
  },
  "youlai-aspnet": {
    title: "youlai-aspnet",
    stack: ".NET 8 + ASP.NET Core 8 + JWT + Redis + MySQL",
    summary:
      "配套 vue3-element-admin 的 .NET 后端实现，性能与生态同步升级，提供 RBAC 权限治理与核心系统模块，并支持 JWT 与 Redis 会话模式。",
    repoUrl: "https://github.com/youlaitech/youlai-aspnet",
  },
  "youlai-boot-tenant": {
    title: "youlai-boot-tenant",
    stack: "JDK 17 + Spring Boot 3 + Spring Security + MyBatis-Plus + JWT + Redis + MySQL",
    summary:
      "youlai-boot 的多租户版本，基于单库多租户方案实现租户隔离，提供精细化 RBAC 权限控制，适合 SaaS 场景的快速落地。",
    repoUrl: "https://github.com/youlaitech/youlai-boot-tenant",
  },
};

const introPopupVisible = ref(false);
const currentProjectKey = ref<ProjectIntroKey>("vue3-element-admin");
const currentProject = computed(() => projectIntros[currentProjectKey.value]);

const openProjectIntro = (key: ProjectIntroKey) => {
  currentProjectKey.value = key;
  introPopupVisible.value = true;
};

const goCurrentProjectRepo = () => {
  if (!currentProject.value) return;
  openUrl(currentProject.value.repoUrl);
};
const getYear = () => {
  return new Date().getFullYear();
};

const openUrl = (url: string) => {
  // #ifdef H5
  window.open(url, "_blank");
  // #endif

  // #ifndef H5
  uni.setClipboardData({ data: url });
  // #endif
};

const copyText = (text: string) => {
  uni.setClipboardData({ data: text });
};

onMounted(() => {
  // #ifdef MP-WEIXIN
  const appBaseInfo =
    typeof uni.getAppBaseInfo === "function" ? uni.getAppBaseInfo() : uni.getSystemInfoSync();
  if (appBaseInfo.appVersion) {
    version.value = appBaseInfo.appVersion;
  }
  // #endif
});
</script>

<style lang="scss" scoped>
.about {
  :deep(.wd-cell__title) {
    max-width: 360rpx;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.about__header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx 28rpx 28rpx;
}

.about__logo {
  width: 140rpx;
  height: 140rpx;
  margin-bottom: 20rpx;
}

.about__info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.about__app-title {
  display: block;
  margin-bottom: 8rpx;
  font-size: 36rpx;
  font-weight: 700;
}

.about__app-version {
  display: block;
  font-size: 24rpx;
  color: var(--color-text-secondary);
}

.about__intro-title {
  display: block;
  margin-bottom: 8rpx;
  font-size: 28rpx;
  font-weight: 500;
}

.about__intro-desc {
  display: block;
  font-size: 24rpx;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.about__intro {
  padding: 0 28rpx 28rpx;
}

.about__footer {
  padding: 32rpx 0;
  text-align: center;
}

.about__copyright {
  display: block;
  font-size: 24rpx;
  color: var(--color-text-placeholder);

  &--sub {
    margin-top: 8rpx;
  }
}

.about__popup {
  padding: 24rpx;
}

.about__popup-title {
  font-size: 32rpx;
  font-weight: 700;
}

.about__popup-stack,
.about__popup-summary {
  margin-top: 12rpx;
  font-size: 26rpx;
  color: var(--color-text-secondary);
}

.about__popup-action {
  margin-top: 20rpx;
}
</style>
