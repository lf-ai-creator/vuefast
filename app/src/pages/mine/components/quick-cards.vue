<template>
  <view class="quick-cards">
    <view class="quick-card" @click="emit('profile')">
      <view class="quick-card__icon quick-card__icon--info">
        <wd-icon name="user" size="28" color="var(--color-primary)" />
      </view>
      <view class="quick-card__body">
        <text class="quick-card__title">我的资料</text>
        <text class="quick-card__desc">修改个人信息</text>
      </view>
    </view>
    <view class="quick-card" @click="emit('account')">
      <view class="quick-card__icon quick-card__icon--success">
        <wd-icon name="safe" size="28" color="var(--color-success)" />
      </view>
      <view class="quick-card__body">
        <text class="quick-card__title">账号安全</text>
        <text class="quick-card__desc">修改密码 / 账号绑定</text>
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
const emit = defineEmits<{
  profile: [];
  account: [];
}>();
</script>

<style lang="scss" scoped>
.quick-cards {
  position: relative;
  z-index: var(--z-sticky);
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  margin-top: 24rpx;
  margin-bottom: 0;
}

.quick-card {
  display: flex;
  gap: 20rpx;
  align-items: center;
  padding: 28rpx 24rpx;
  background: var(--color-bg-card);
  border-radius: 24rpx;
  box-shadow: var(--shadow-sm);
}

.quick-card:active {
  box-shadow: var(--shadow-sm);
  transform: scale(0.96);
}

.quick-card__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 84rpx;
  height: 84rpx;
  border-radius: 22rpx;

  &--info {
    background: var(--color-primary-light);
  }

  &--success {
    background: var(--color-success-light);
  }
}

.quick-card__body {
  flex: 1;
  min-width: 0;
}

.quick-card__title {
  display: block;
  overflow: hidden;
  font-size: 28rpx;
  font-weight: 500;
  line-height: 1.35;
  color: var(--color-text);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.quick-card__desc {
  display: block;
  margin-top: 8rpx;
  overflow: hidden;
  font-size: 22rpx;
  line-height: 1.6;
  color: var(--color-text-secondary);
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
