<template>
  <view class="scan-confirm">
    <custom-navbar title="扫码登录确认" placeholder />

    <view class="scan-confirm__body">
      <view class="scan-confirm__card">
        <image class="scan-confirm__logo" src="/static/images/logo.png" mode="aspectFit" />
        <text class="scan-confirm__tip">PC 端扫码登录</text>
        <text class="scan-confirm__user">{{ scanResult?.nickname || "未知用户" }}</text>
        <text class="scan-confirm__hint">是否确认在 PC 端登录？</text>

        <view class="scan-confirm__actions">
          <wd-button
            type="error"
            plain
            block
            :disabled="!scanResult"
            :loading="isCancelling"
            @click="handleCancel"
          >
            取消登录
          </wd-button>
          <wd-button block :disabled="!scanResult" :loading="isLoading" @click="handleConfirm">
            确认登录
          </wd-button>
        </view>
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { onLoad } from "@dcloudio/uni-app";
import { useToast } from "@wot-ui/ui";
import { getErrorMessage } from "@/utils/error";
import AuthAPI, { type QrCodeScanResult } from "@/api/auth";

definePage({
  name: "scan-confirm",
  style: { navigationStyle: "custom", navigationBarTitleText: "" },
  layout: "blank",
});

const toast = useToast();

// toast 停留时长，读完提示再返回上一页
const TOAST_DURATION = 800;

// 确认按钮 loading 态，防止连点重复确认
const isLoading = ref(false);
// 取消按钮 loading 态，防止连点重复取消
const isCancelling = ref(false);
// 从扫码入口经 query 传入的票据
const ticket = ref("");
// scan 接口返回的脱敏用户信息，请求完成前按钮保持禁用
const scanResult = ref<QrCodeScanResult | null>(null);

// 进入页面先标记已扫码，让 PC 端立即显示「已扫码」并展示头像/昵称
const markScanned = async (code: string) => {
  try {
    scanResult.value = await AuthAPI.markQrLoginScanned(code);
  } catch (error) {
    toast.error(getErrorMessage(error, "二维码无效或已过期"));
    setTimeout(() => uni.navigateBack(), TOAST_DURATION);
  }
};

// 用户点击「确认登录」：授权 PC 端用该票据换取会话
const handleConfirm = async () => {
  if (isLoading.value) return;
  isLoading.value = true;
  try {
    await AuthAPI.confirmQrLogin(ticket.value);
    toast.success("已确认登录");
    setTimeout(() => uni.navigateBack(), TOAST_DURATION);
  } catch (error) {
    toast.error(getErrorMessage(error, "确认失败"));
  } finally {
    isLoading.value = false;
  }
};

// 用户点击「取消登录」：撤回扫码，PC 端状态变为 CANCELED
const handleCancel = async () => {
  if (isCancelling.value) return;
  isCancelling.value = true;
  try {
    await AuthAPI.cancelQrLogin(ticket.value);
    toast.info("已取消登录");
  } catch {
    // 取消失败不影响返回
  } finally {
    setTimeout(() => uni.navigateBack(), TOAST_DURATION);
  }
};

onLoad((options) => {
  const code = options?.ticket ? decodeURIComponent(options.ticket) : "";
  if (!code) {
    toast.error("二维码无效");
    setTimeout(() => uni.navigateBack(), TOAST_DURATION);
    return;
  }
  ticket.value = code;
  markScanned(code);
});
</script>

<style lang="scss" scoped>
.scan-confirm {
  min-height: 100vh;
  background: var(--color-bg-card);

  &__body {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 48rpx 64rpx 0;
  }

  &__card {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    padding: 64rpx 48rpx;
    background: var(--color-bg-card);
    border: 2rpx solid var(--color-border-light);
    border-radius: 32rpx;
    box-shadow: var(--shadow-float);
  }

  &__logo {
    width: 96rpx;
    height: 96rpx;
    margin-bottom: 24rpx;
  }

  &__tip {
    font-size: 28rpx;
    color: var(--color-text-secondary);
  }

  &__user {
    margin: 16rpx 0;
    font-size: 40rpx;
    font-weight: 700;
    color: var(--color-text);
  }

  &__hint {
    margin-bottom: 48rpx;
    font-size: 26rpx;
    color: var(--color-text-placeholder);
  }

  &__actions {
    display: flex;
    gap: 24rpx;
    width: 100%;
  }
}
</style>
