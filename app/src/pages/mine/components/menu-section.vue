<template>
  <view class="menu-section">
    <text class="menu-section__title">{{ title }}</text>
    <view class="menu-list">
      <view
        v-for="item in items"
        :key="item.key"
        class="menu-row"
        @click="emit('select', item.key)"
      >
        <view class="menu-row__icon" :class="`menu-row__icon--${item.tone}`">
          <wd-icon :name="item.icon" size="18" :color="iconColors[item.tone]" />
        </view>
        <view class="menu-row__main">
          <text class="menu-row__title">{{ item.title }}</text>
          <text class="menu-row__desc">{{ item.desc }}</text>
        </view>
        <text v-if="item.value" class="menu-row__value">{{ item.value }}</text>
        <wd-icon name="right" size="16" color="var(--color-text-placeholder)" />
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
export interface MenuItem {
  key: string;
  icon: string;
  tone: "primary" | "warning" | "danger" | "success" | "info";
  title: string;
  desc: string;
  value?: string;
}

const iconColors: Record<MenuItem["tone"], string> = {
  primary: "var(--color-primary)",
  warning: "var(--color-primary)",
  danger: "var(--color-danger)",
  success: "var(--color-success)",
  info: "var(--color-info)",
};

defineProps<{
  title: string;
  items: MenuItem[];
}>();

const emit = defineEmits<{
  select: [key: string];
}>();
</script>

<style lang="scss" scoped>
.menu-section {
  padding: 28rpx;
  background: var(--color-bg-card);
  border-radius: 32rpx;
  box-shadow: var(--shadow-md);

  &__title {
    display: block;
    margin-bottom: 18rpx;
    font-size: 26rpx;
    font-weight: 600;
    color: var(--color-text);
  }
}

.menu-list {
  overflow: hidden;
}

.menu-row {
  display: flex;
  gap: 20rpx;
  align-items: center;
  padding: 24rpx 20rpx;
  background: transparent;
}

.menu-row + .menu-row {
  border-top: 1rpx solid var(--color-border-light);
}

.menu-row__icon {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 72rpx;
  height: 72rpx;
  border-radius: 22rpx;

  &--primary,
  &--warning {
    background: var(--color-primary-alpha-15);
  }

  &--danger {
    background: var(--color-danger-light);
  }

  &--success {
    background: var(--color-success-light);
  }

  &--info {
    background: var(--color-info-light);
  }
}

.menu-row__main {
  flex: 1;
  min-width: 0;
}

.menu-row__title {
  display: block;
  font-size: 26rpx;
  font-weight: 500;
  color: var(--color-text);
}

.menu-row__desc {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: var(--color-text-secondary);
}

.menu-row__value {
  margin-left: 12rpx;
  font-size: 22rpx;
  color: var(--color-text-placeholder);
}
</style>
