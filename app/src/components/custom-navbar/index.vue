<template>
  <view v-if="fixed && placeholder" :style="{ height: totalHeight + 'px' }" />
  <view
    class="custom-navbar"
    :class="{ 'custom-navbar--fixed': fixed }"
    :style="{
      height: totalHeight + 'px',
      paddingTop: statusBarHeight + 'px',
      background: bgColor,
    }"
  >
    <view class="custom-navbar__content" :style="{ height: contentHeight + 'px' }">
      <view class="custom-navbar__left" :style="{ width: leftWidth + 'px' }">
        <view v-if="showBack" class="custom-navbar__back" @click="handleBack">
          <wd-icon :name="backIcon" :size="backIconSize" :color="iconColor" />
        </view>

        <view v-if="showHome" class="custom-navbar__home" @click="handleHome">
          <wd-icon name="home" :size="backIconSize" :color="iconColor" />
        </view>

        <slot name="left" />
      </view>

      <view class="custom-navbar__center">
        <text v-if="title" class="custom-navbar__title" :style="{ color: titleColor }">
          {{ title }}
        </text>
        <slot name="center" />
      </view>

      <view class="custom-navbar__right" :style="{ width: rightWidth + 'px' }">
        <slot name="right" />
        <!-- 微信端胶囊按钮占位，保证插槽内容不会顶到胶囊下方 -->
        <view class="custom-navbar__capsule-space" :style="{ width: capsuleSpaceWidth + 'px' }" />
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useNavbar } from "@/composables/useNavbar";

interface Props {
  title?: string;
  titleColor?: string;
  /** 背景色或渐变，取值同 background 简写属性 */
  bgColor?: string;
  showBack?: boolean;
  showHome?: boolean;
  backIcon?: string;
  backIconSize?: string;
  iconColor?: string;
  fixed?: boolean;
  placeholder?: boolean;
  navBarHeight?: number;
}

const props = withDefaults(defineProps<Props>(), {
  title: "",
  titleColor: "var(--color-text)",
  bgColor: "var(--color-bg-card)",
  showBack: true,
  showHome: false,
  backIcon: "arrow-left",
  backIconSize: "40rpx",
  iconColor: "var(--color-text)",
  fixed: true,
  placeholder: false,
  navBarHeight: 44,
});

const emit = defineEmits<{
  (e: "back"): void;
  (e: "home"): void;
}>();

const navbar = useNavbar({ navBarHeight: props.navBarHeight });

const fixed = computed(() => props.fixed);
const placeholder = computed(() => props.placeholder);

const statusBarHeight = computed(() => navbar.statusBarHeight.value);
const navBarHeight = computed(() => navbar.navBarHeight);
const totalHeight = computed(() => navbar.totalHeight.value);

const contentHeight = computed(() => {
  const height = totalHeight.value - statusBarHeight.value;
  return height > 0 ? height : navBarHeight.value;
});

const menuButtonWidth = computed(() => navbar.menuButtonWidth.value);
const menuButtonRightGap = computed(() => navbar.menuButtonRightGap.value);
const menuButtonLeft = computed(() => navbar.menuButtonLeft.value);

const capsuleSpaceWidth = computed(() => {
  let width = 0;
  // #ifdef MP-WEIXIN
  if (menuButtonWidth.value > 0) {
    width = menuButtonWidth.value + menuButtonRightGap.value;
  }
  // #endif
  return width;
});

const rightContentWidth = computed(() => 96);

const leftWidth = computed(() => {
  let width = 80;
  // #ifdef MP-WEIXIN
  width = menuButtonLeft.value > 0 ? menuButtonLeft.value : 80;
  // #endif
  return width;
});

const rightWidth = computed(() => {
  let width = 80;
  // #ifdef MP-WEIXIN
  width = capsuleSpaceWidth.value + rightContentWidth.value;
  // #endif
  return width;
});

function handleBack() {
  emit("back");

  const pages = getCurrentPages();
  if (pages.length > 1) {
    uni.navigateBack();
  } else {
    uni.switchTab({ url: "/pages/index/index" });
  }
}

function handleHome() {
  emit("home");
  uni.switchTab({ url: "/pages/index/index" });
}
</script>

<script lang="ts">
export default {
  name: "CustomNavbar",
  options: {
    virtualHost: true,
    styleIsolation: "shared",
  },
};
</script>

<style lang="scss" scoped>
.custom-navbar {
  position: relative;
  z-index: var(--z-navbar);
  box-sizing: border-box;
  background-color: var(--color-bg-card);

  &--fixed {
    position: fixed;
    top: 0;
    right: 0;
    left: 0;
  }
}

.custom-navbar__content {
  position: relative;
  z-index: var(--z-dropdown);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16rpx;
}

.custom-navbar__left {
  z-index: var(--z-dropdown);
  display: flex;
  align-items: center;
}

.custom-navbar__back,
.custom-navbar__home {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64rpx;
  height: 64rpx;
  margin-right: 8rpx;
  border-radius: 50%;

  &:active {
    background-color: var(--color-fill-2);
  }
}

.custom-navbar__center {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: var(--z-dropdown);
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 50%;
  overflow: hidden;
  transform: translate(-50%, -50%);
}

.custom-navbar__title {
  z-index: var(--z-dropdown);
  overflow: hidden;
  font-size: 32rpx;
  color: var(--color-text);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.custom-navbar__right {
  z-index: var(--z-dropdown);
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.custom-navbar__capsule-space {
  flex: 0 0 auto;
  height: 2rpx;
}
</style>
