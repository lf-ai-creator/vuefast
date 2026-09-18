<template>
  <view>
    <view class="py-24rpx px-32rpx">
      <text class="network__tip-text">
        温馨提示：点击下方「开始测试」按钮，即可自动检测当前网络延迟。
      </text>
    </view>

    <view class="px-32rpx">
      <wd-button block plain @click="startTest">开始测试</wd-button>
    </view>

    <view v-if="isTesting" class="network__loading">
      <wd-loading color="var(--wot-color-theme)" />
      <text class="network__loading-text">正在测试中...</text>
    </view>

    <view v-if="result !== null" class="px-32rpx">
      <view class="result-card">
        <view class="result-card__header">测试结果</view>
        <view class="result-card__row">
          <text style="color: var(--color-text-secondary)">网络延迟</text>
          <text :class="['text-36rpx font-600', statusColor]">{{ result }}ms</text>
        </view>
        <view class="result-card__row">
          <text style="color: var(--color-text-secondary)">网络状态</text>
          <text :class="['font-500', statusColor]">{{ statusText }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { onLoad } from "@dcloudio/uni-app";

definePage({
  name: "network",
  style: { navigationBarTitleText: "网络检测" },
});

const result = ref<number | null>(null);
const isTesting = ref(false);

const statusText = computed(() => {
  if (result.value == null) return "";
  if (result.value < 100) return "优秀";
  if (result.value < 300) return "良好";
  if (result.value < 500) return "一般";
  return "较差";
});

const statusColor = computed(() => {
  if (result.value == null) return "";
  if (result.value < 100) return "color-success";
  if (result.value < 300) return "color-primary";
  if (result.value < 500) return "color-warning";
  return "color-danger";
});

const startTest = async () => {
  isTesting.value = true;
  result.value = null;
  try {
    const startTime = Date.now();
    // #ifdef MP-WEIXIN
    await new Promise<void>((resolve) => {
      wx.request({
        url: "https://www.baidu.com",
        method: "GET",
        success: () => resolve(),
        fail: () => resolve(),
      });
    });
    // #endif
    // #ifdef H5
    await fetch("https://www.baidu.com", { mode: "no-cors" });
    // #endif
    result.value = Date.now() - startTime;
  } catch {
    result.value = 9999;
  } finally {
    isTesting.value = false;
  }
};

onLoad(() => {
  uni.setNavigationBarTitle({ title: "网络测试" });
});
</script>

<style lang="scss" scoped>
.result-card {
  overflow: hidden;
  background: var(--color-bg-card);
  border: 1rpx solid var(--color-border);
  border-radius: 16rpx;

  &__header {
    padding: 24rpx;
    font-size: 32rpx;
    font-weight: 600;
    border-bottom: 1rpx solid var(--color-border);
  }

  &__row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24rpx;

    & + & {
      border-top: 1rpx solid var(--color-border-light);
    }
  }
}

.network__tip-text {
  font-size: 24rpx;
  color: var(--color-text-placeholder);
}

.network__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx 0;
}

.network__loading-text {
  margin-top: 16rpx;
  font-size: 24rpx;
  color: var(--color-text-secondary);
}
</style>
