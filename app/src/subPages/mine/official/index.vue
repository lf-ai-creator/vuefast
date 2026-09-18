<template>
  <view>
    <view class="brand">
      <image src="/static/images/logo.png" class="brand__logo" mode="aspectFit" />
      <view class="flex-1 min-w-0">
        <view class="brand__title">有来技术</view>
        <view class="brand__desc">让开源项目更加易用</view>
      </view>
    </view>

    <view class="official-tip">
      长按识别下方二维码，关注「有来技术」公众号，获取最新技术分享和项目动态。
    </view>

    <view class="qrcode-card">
      <image src="/static/images/qrcode-official.png" class="qrcode-card__img" mode="aspectFit" />
    </view>

    <view class="qrcode-hint">长按识别二维码关注</view>
  </view>
</template>

<script lang="ts" setup>
import { onLoad } from "@dcloudio/uni-app";

definePage({
  name: "official",
  style: { navigationBarTitleText: "公众号" },
});

onLoad(() => {
  uni.setNavigationBarTitle({ title: "公众号" });
});
</script>

<style lang="scss" scoped>
.brand {
  display: flex;
  gap: 20rpx;
  align-items: center;
  padding: 28rpx;
  background: var(--color-bg-card);
  border-radius: 20rpx;
  box-shadow: var(--shadow-sm);
}

.brand__logo {
  width: 96rpx;
  height: 96rpx;
  border-radius: 20rpx;
}

.brand__title {
  font-size: 34rpx;
  font-weight: 700;
  color: var(--color-text);
}

.brand__desc {
  margin-top: 8rpx;
  font-size: 26rpx;
  color: var(--color-text-secondary);
}

.official-tip {
  padding: 20rpx;
  margin-top: 20rpx;
  font-size: 26rpx;
  line-height: 1.6;
  color: var(--color-text);
  background: var(--color-fill-1);
  border-radius: 16rpx;
}

.qrcode-card {
  padding: 28rpx;
  margin-top: 24rpx;
  background: var(--color-bg-card);
  border-radius: 20rpx;
  box-shadow: var(--shadow-sm);
}

.qrcode-card__img {
  width: 100%;
  border-radius: 16rpx;
}

.qrcode-hint {
  margin-top: 20rpx;
  font-size: 26rpx;
  color: var(--color-text-secondary);
  text-align: center;
}
</style>
