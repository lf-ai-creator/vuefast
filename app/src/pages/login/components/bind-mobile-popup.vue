<template>
  <wd-popup
    v-model="visible"
    position="bottom"
    closable
    custom-class="popup-bottom"
    @close="handleClose"
  >
    <view class="p-48rpx">
      <text class="bind-mobile__title">绑定手机号</text>

      <view class="bind-mobile__form">
        <view class="bind-mobile__field">
          <wd-icon name="phone" size="20" color="var(--color-text-placeholder)" />
          <input
            v-model="mobile"
            class="bind-mobile__input"
            placeholder="请输入手机号"
            type="number"
            :maxlength="11"
          />
        </view>

        <view class="bind-mobile__field">
          <wd-icon name="lock" size="20" color="var(--color-text-placeholder)" />
          <input
            v-model="code"
            class="bind-mobile__input"
            placeholder="请输入验证码"
            type="number"
            :maxlength="6"
          />
          <view
            class="bind-mobile__code-btn"
            :class="
              countdown > 0 ? 'bind-mobile__code-btn--disabled' : 'bind-mobile__code-btn--active'
            "
            @click="handleSendCode"
          >
            {{ countdown > 0 ? `${countdown}s` : "获取验证码" }}
          </view>
        </view>

        <!-- 演示环境提示 -->
        <view class="bind-mobile__demo-hint">
          <text class="bind-mobile__demo-hint-text">演示环境验证码：123456</text>
        </view>

        <wd-button block :loading="isSubmitting" @click="handleConfirm">确认绑定</wd-button>
      </view>
    </view>
  </wd-popup>
</template>

<script lang="ts">
export default {
  options: { styleIsolation: "shared" },
};
</script>

<script setup lang="ts">
import { ref } from "vue";
import { useToast } from "@wot-ui/ui";
import { useSmsLoginCode, isValidMobile } from "@/composables/useSmsLoginCode";
import { useUserStore } from "@/store/modules/user";
import { getErrorMessage } from "@/utils/error";

/** 微信静默登录后需绑定手机号时，由父组件打开本弹窗 */
const visible = defineModel<boolean>({ required: true });

const emit = defineEmits<{
  /** 绑定成功（会话已就绪），父组件负责跳转 */
  (e: "success"): void;
}>();

const toast = useToast();
const userStore = useUserStore();
const { countdown, sendCode, resetCountdown } = useSmsLoginCode();

const mobile = ref("18888888888");
const code = ref("");
const isSubmitting = ref(false);
/** 待绑定的微信 openid，由父组件通过 open 传入 */
let openid = "";

/** 打开弹窗并记录待绑定的 openid */
function open(boundOpenid: string) {
  openid = boundOpenid;
  mobile.value = "18888888888";
  code.value = "";
  visible.value = true;
}

function handleClose() {
  resetCountdown();
  code.value = "";
}

async function handleSendCode() {
  await sendCode(mobile.value);
}

async function handleConfirm() {
  if (isSubmitting.value) return;
  if (!isValidMobile(mobile.value)) {
    toast.error("请输入正确的手机号");
    return;
  }
  if (!code.value.trim()) {
    toast.error("请输入验证码");
    return;
  }
  isSubmitting.value = true;
  try {
    await userStore.bindMobileForWxMa({ openid, mobile: mobile.value, smsCode: code.value });
    await userStore.loadUserInfo();
    visible.value = false;
    toast.success("绑定成功");
    emit("success");
  } catch (error) {
    toast.error(getErrorMessage(error, "绑定失败"));
  } finally {
    isSubmitting.value = false;
  }
}

defineExpose({ open });
</script>

<style lang="scss" scoped>
.bind-mobile__title {
  display: block;
  margin-bottom: 48rpx;
  font-size: 36rpx;
  font-weight: 600;
  color: var(--color-text);
  text-align: center;
}

.bind-mobile__field {
  display: flex;
  align-items: center;
  height: 88rpx;
  padding: 0 32rpx;
  margin-top: 24rpx;
  background-color: var(--color-fill-1);
  border-radius: 24rpx;
}

.bind-mobile__input {
  flex: 1;
  height: 100%;
  margin-left: 24rpx;
  font-size: 28rpx;
  color: var(--color-text);
}

.bind-mobile__code-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 64rpx;
  padding: 0 32rpx;
  font-size: 28rpx;
  font-weight: 500;
  border-radius: 16rpx;

  &--active {
    color: var(--color-primary);
    background-color: var(--color-primary-light);
  }

  &--disabled {
    color: var(--color-text-placeholder);
    background-color: var(--color-fill-1);
  }
}

.bind-mobile__demo-hint {
  display: flex;
  justify-content: center;
  margin-top: 24rpx;
}

.bind-mobile__demo-hint-text {
  padding: 8rpx 24rpx;
  font-size: 24rpx;
  color: var(--color-warning);
  background-color: var(--color-warning-light);
  border-radius: 8rpx;
}
</style>

<style lang="scss">
/* 暗黑模式覆盖 - 非 scoped，因 .wot-theme-dark 位于页面根元素 */
.wot-theme-dark {
  .bind-mobile__field {
    background-color: rgba(255, 255, 255, 0.06);
  }
}
</style>
