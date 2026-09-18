<template>
  <view class="community-card" @click="emit('open')">
    <image class="community-card__bg" src="/static/images/official-bg.png" mode="aspectFill" />
    <view class="community-card__mask" />
    <view class="community-card__logo">
      <image src="/static/images/logo.png" mode="aspectFit" class="w-full h-full" />
    </view>
    <view class="community-card__body">
      <view class="community-card__title-row">
        <text class="community-card__title">关注有来技术</text>
        <wd-tag type="success" plain custom-class="community-card__tag">官方社区</wd-tag>
      </view>
      <text class="community-card__desc">开源更新、实战内容、交流群入口，统一在这里查看</text>
    </view>
    <view class="community-card__arrow">
      <wd-icon name="right" size="16" color="var(--color-text-secondary)" />
    </view>
  </view>
</template>

<script lang="ts" setup>
const emit = defineEmits<{
  open: [];
}>();
</script>

<style lang="scss" scoped>
.community-card {
  position: relative;
  display: flex;
  gap: 24rpx;
  align-items: center;
  padding: 36rpx;
  overflow: hidden;
  background: transparent;
  border-radius: 32rpx;
  box-shadow: var(--shadow-md);
}

.community-card__bg {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: var(--z-base);
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 1;
}

.community-card__mask {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: var(--z-mask);
  background: linear-gradient(
    90deg,
    var(--color-media-mask) 0%,
    var(--color-media-mask-light) 55%,
    var(--color-media-mask) 100%
  );
}

.community-card__logo {
  position: relative;
  z-index: var(--z-content);
  box-sizing: border-box;
  width: 84rpx;
  height: 84rpx;
  padding: 10rpx;
  background: var(--color-bg-card-alpha-95);
  border: 1rpx solid var(--color-border-glass);
  border-radius: 20rpx;
  box-shadow: var(--shadow-sm);
}

.community-card__body {
  position: relative;
  z-index: var(--z-content);
  flex: 1;
  min-width: 0;
}

.community-card__arrow {
  position: relative;
  z-index: var(--z-content);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44rpx;
  height: 44rpx;
  background: var(--color-glass);
  border-radius: 999rpx;
}

.community-card__title-row {
  display: flex;
  gap: 16rpx;
  align-items: center;
  margin-top: 14rpx;
}

.community-card__title {
  flex-shrink: 0;
  font-size: 32rpx;
  font-weight: 600;
  line-height: 1;
  color: var(--color-text);
  letter-spacing: 0.4rpx;
}

/* wd-tag 外层是自定义组件节点，压掉其行高避免与标题错位 */
.community-card__tag {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  line-height: 1;
}

.community-card__desc {
  display: -webkit-box;
  margin-top: 10rpx;
  overflow: hidden;
  font-size: 24rpx;
  line-height: 1.55;
  color: var(--color-text-secondary);
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}
</style>
