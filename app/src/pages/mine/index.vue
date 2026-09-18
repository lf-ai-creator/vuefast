<template>
  <view>
    <view class="mine-hero" :style="{ paddingTop: `${navbar.totalHeight.value}px` }">
      <custom-navbar
        :bg-color="isScrolled ? headerBackground : 'transparent'"
        title-color="var(--color-text-inverse)"
        icon-color="var(--color-text-inverse)"
        :show-back="false"
        :placeholder="false"
      >
        <template #center>
          <text class="mine-navbar__title">个人中心</text>
        </template>
      </custom-navbar>

      <view class="mine-hero__content">
        <profile-card
          :is-authenticated="isAuthenticated"
          :avatar="avatar"
          :name="displayName"
          :username="username"
          :dept-name="deptName"
          @profile="openProfile"
          @login="navigateToLogin"
          @scan="scanLogin"
        />

        <view class="community-slot">
          <view class="community-slot__bg" :style="{ background: headerBackground }" />
          <community-card @open="openOfficialAccount" />
        </view>

        <quick-cards v-if="isAuthenticated" @profile="openProfile" @account="openAccount" />
      </view>
    </view>

    <view class="mine-body">
      <menu-section title="系统工具" :items="toolMenus" @select="handleMenuSelect" />
      <menu-section title="帮助与支持" :items="helpMenus" @select="handleMenuSelect" />

      <wd-button
        v-if="isAuthenticated"
        type="danger"
        variant="plain"
        size="large"
        block
        @click="confirmLogout"
      >
        退出登录
      </wd-button>
    </view>

    <wd-loading
      v-if="isClearing"
      v-model="isClearing"
      text="正在清理..."
      mask
      custom-class="loading-center"
    />
  </view>
</template>

<script lang="ts" setup>
import { computed, ref } from "vue";
import { onPageScroll, onShow } from "@dcloudio/uni-app";
import { storeToRefs } from "pinia";
import { useUserStore, useThemeStore } from "@/store";
import { useRouter } from "uni-mini-router";
import { useNavbar } from "@/composables/useNavbar";
import { useScanLogin } from "@/composables/useScanLogin";
import { useLogout } from "@/composables/useLogout";
import { useCacheCleaner } from "@/composables/useCacheCleaner";
import ProfileCard from "./components/profile-card.vue";
import CommunityCard from "./components/community-card.vue";
import QuickCards from "./components/quick-cards.vue";
import MenuSection, { type MenuItem } from "./components/menu-section.vue";

definePage({
  name: "mine",
  style: { navigationStyle: "custom" },
  layout: "tabbar",
});

const userStore = useUserStore();
const themeStore = useThemeStore();
const router = useRouter();
const navbar = useNavbar({ hasTabbar: true });
const { scanLogin } = useScanLogin();
const { confirmLogout } = useLogout();

/** 滚动后导航栏补上渐变背景，否则内容会从透明导航栏下穿过 */
const isScrolled = ref(false);
onPageScroll(({ scrollTop }) => {
  isScrolled.value = scrollTop > 0;
});

const { isAuthenticated } = storeToRefs(userStore);
const userInfo = computed(() => userStore.userInfo);
const defaultAvatar = "/static/images/default-avatar.png";

const avatar = computed(() =>
  isAuthenticated.value && userInfo.value?.avatar ? userInfo.value.avatar : defaultAvatar
);
const displayName = computed(() =>
  isAuthenticated.value ? userInfo.value?.nickname || "匿名用户" : "欢迎使用"
);
const username = computed(() => userInfo.value?.username || "未设置账号");
const deptName = computed(() => (isAuthenticated.value ? userInfo.value?.deptName || "" : ""));

const headerBackground = computed(() => {
  const color = themeStore.themeVars.colorTheme || "var(--color-primary)";
  const colorWithAlpha = color.length === 7 ? `${color}E6` : color;
  const colorWithAlpha2 = color.length === 7 ? `${color}CC` : color;
  return `linear-gradient(135deg, ${colorWithAlpha} 0%, ${colorWithAlpha2} 100%)`;
});

const appVersion = ref("1.0.0");
const {
  usageText: storageUsageText,
  isClearing,
  loadUsage: loadStorageUsage,
  clear: clearCache,
} = useCacheCleaner();

// 常用功能在前，维护操作在后
const toolMenus = computed<MenuItem[]>(() => [
  {
    key: "notice",
    icon: "notification",
    tone: "primary",
    title: "消息通知",
    desc: "查看系统通知与公告",
  },
  { key: "theme", icon: "settings", tone: "primary", title: "主题设置", desc: "主题色与明暗模式" },
  {
    key: "network",
    icon: "wifi",
    tone: "primary",
    title: "网络检测",
    desc: "检测网络与服务器连接",
  },
  {
    key: "clear-cache",
    icon: "delete",
    tone: "danger",
    title: "清理缓存",
    desc: "释放本地存储空间",
    value: storageUsageText.value,
  },
]);

const helpMenus = computed<MenuItem[]>(() => [
  {
    key: "agreement",
    icon: "file",
    tone: "success",
    title: "用户协议",
    desc: "了解产品使用规则",
  },
  {
    key: "about",
    icon: "info-circle",
    tone: "info",
    title: "关于系统",
    desc: "产品介绍与联系方式",
    value: `v${appVersion.value}`,
  },
]);

const menuRoutes: Record<string, string> = {
  notice: "/subPages/work/notice/index",
  network: "/subPages/mine/settings/network/index",
  theme: "/subPages/mine/settings/theme/index",
  agreement: "/subPages/mine/settings/agreement/index",
  about: "/subPages/mine/about/index",
};

function handleMenuSelect(key: string) {
  if (key === "clear-cache") {
    clearCache();
    return;
  }
  if (key === "notice" && !isAuthenticated.value) {
    navigateToLogin();
    return;
  }
  const path = menuRoutes[key];
  if (path) {
    router.push({ path });
  }
}

// 登录
const navigateToLogin = () => {
  const pages = getCurrentPages();
  const currentPage = pages[pages.length - 1];
  const currentPagePath = `/${currentPage.route}`;
  router.push({ path: "/pages/login/index", query: { redirect: currentPagePath } });
};

const openProfile = () => {
  if (!isAuthenticated.value) {
    navigateToLogin();
    return;
  }
  router.push({ path: "/subPages/mine/profile/index" });
};

// 账号和安全
const openAccount = () => {
  if (!isAuthenticated.value) {
    navigateToLogin();
    return;
  }
  router.push({ path: "/subPages/mine/account/index" });
};

// 有来技术公众号
const openOfficialAccount = () => {
  uni.navigateTo({
    url: "/subPages/mine/official/index",
  });
};

const hasUserProfile = computed(() => {
  const info = userInfo.value;
  return !!(info && (info.userId || info.username || info.nickname));
});

const loadUserInfoIfNeeded = async () => {
  // 已登录但资料未加载时补拉（loadUserInfo），专治「token 在、userInfo 空」的断档态
  if (!isAuthenticated.value || hasUserProfile.value) return;
  try {
    await userStore.loadUserInfo();
  } catch {
    // ignore
  }
};

const syncMiniProgramVersion = () => {
  // #ifdef MP-WEIXIN
  appVersion.value = uni.getAccountInfoSync().miniProgram.version || "1.0.0";
  // #endif
};

onShow(async () => {
  await loadUserInfoIfNeeded();
  await loadStorageUsage();
  syncMiniProgramVersion();
});
</script>

<style lang="scss" scoped>
.mine-hero {
  position: relative;
  padding-bottom: 24rpx;
  overflow: visible;
}

/* 渐变以社区卡片为锚点：底边压在卡片中线、上沿穿到导航栏后面，形成卡片被背景分割的效果 */
.community-slot {
  position: relative;
}

.community-slot__bg {
  position: absolute;
  right: -28rpx;
  bottom: 50%;
  left: -28rpx;
  z-index: -1;
  height: 800rpx;
  pointer-events: none;
}

.mine-hero__content {
  position: relative;
  z-index: var(--z-sticky);
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding: 20rpx 28rpx 0;
}

.mine-navbar__title {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--color-text-inverse);
  letter-spacing: 2rpx;
}

.mine-body {
  position: relative;
  z-index: var(--z-base);
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  padding: 0 28rpx 40rpx;
  margin-top: 0;
  background: var(--color-bg-page);
  border-top-left-radius: 48rpx;
  border-top-right-radius: 48rpx;
}

.loading-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--color-overlay);
  border-radius: 24rpx;
}
</style>
