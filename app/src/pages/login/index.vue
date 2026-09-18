<template>
  <view class="login">
    <!-- 背景装饰 -->
    <view class="login__decoration">
      <view class="login__circle login__circle--1" />
      <view class="login__circle login__circle--2" />
    </view>

    <!-- 导航栏：透明悬浮于渐变背景上，返回逻辑由组件内聚（栈空时回首页） -->
    <custom-navbar bg-color="transparent" placeholder />

    <!-- 主内容 -->
    <view class="login__body">
      <!-- Logo -->
      <view class="login__brand">
        <view class="login__logo-box">
          <image class="login__logo" src="/static/images/logo.png" mode="aspectFit" />
        </view>
        <text class="login__brand-name">youlai-app</text>
      </view>

      <!-- 登录卡片 -->
      <view class="login__card">
        <!-- 标题 -->
        <view class="login__card-head">
          <text class="login__card-title">欢迎登录</text>
          <text class="login__card-subtitle">{{ loginModeDesc }}</text>
        </view>

        <!-- 表单区域 -->
        <wd-form
          v-if="loginMode !== 'WECHAT'"
          ref="loginFormRef"
          :model="formData"
          :schema="formSchema"
          error-type="message"
          hide-asterisk
        >
          <!-- 用户名/手机号 -->
          <wd-form-item prop="username" layout="vertical">
            <view class="login__field">
              <wd-icon name="user" size="20" color="var(--color-text-placeholder)" />
              <input
                v-model="formData.username"
                class="login__field-input"
                :placeholder="loginMode === 'PASSWORD' ? '请输入用户名' : '请输入手机号'"
                :maxlength="loginMode === 'PASSWORD' ? 50 : 11"
              />
            </view>
          </wd-form-item>

          <!-- 密码 -->
          <wd-form-item v-if="loginMode === 'PASSWORD'" prop="password" layout="vertical">
            <view class="login__field">
              <wd-icon name="lock" size="20" color="var(--color-text-placeholder)" />
              <input
                v-model="formData.password"
                class="login__field-input"
                placeholder="请输入密码"
                :maxlength="50"
                :password="!isPwdVisible"
                @confirm="handleLogin"
              />
              <wd-icon
                :name="isPwdVisible ? 'eye' : 'eye-invisible'"
                size="20"
                color="var(--color-text-placeholder)"
                class="login__field-suffix"
                @click="isPwdVisible = !isPwdVisible"
              />
            </view>
          </wd-form-item>

          <!-- 图形验证码（密码登录时显示） -->
          <wd-form-item v-if="loginMode === 'PASSWORD'" prop="captchaCode" layout="vertical">
            <view class="login__field">
              <wd-icon name="code-square" size="20" color="var(--color-text-placeholder)" />
              <input
                v-model="formData.captchaCode"
                class="login__field-input"
                placeholder="请输入验证码"
                :maxlength="6"
                @confirm="handleLogin"
              />
              <image
                v-if="captchaBase64"
                class="login__captcha-img"
                :src="captchaBase64"
                mode="aspectFit"
                @click="loadCaptcha"
              />
            </view>
          </wd-form-item>

          <!-- 短信验证码 -->
          <wd-form-item v-if="loginMode === 'SMS'" prop="code" layout="vertical">
            <view class="login__field">
              <wd-icon name="lock" size="20" color="var(--color-text-placeholder)" />
              <input
                v-model="formData.code"
                class="login__field-input"
                placeholder="请输入验证码"
                type="number"
                :maxlength="6"
                @confirm="handleLogin"
              />
              <view
                class="login__code-btn"
                :class="smsCountdown > 0 ? 'login__code-btn--disabled' : 'login__code-btn--active'"
                @click="handleSendCode"
              >
                {{ smsCountdown > 0 ? `${smsCountdown}s` : "获取验证码" }}
              </view>
            </view>
          </wd-form-item>

          <!-- 演示环境提示 -->
          <view v-if="loginMode === 'SMS'" class="login__form-item login__demo-hint">
            <text class="login__demo-hint-text">演示环境验证码：123456</text>
          </view>

          <!-- 登录按钮 -->
          <view class="login__form-item">
            <wd-button block :loading="isLoggingIn" @click="handleLogin">登 录</wd-button>
          </view>

          <!-- 切换登录方式 -->
          <view class="login__form-item login__mode-switch" @click="toggleLoginMode">
            <text class="login__mode-switch-text">
              {{ loginMode === "PASSWORD" ? "忘记密码？" : "记得密码？" }}
            </text>
            <text class="login__mode-switch-link">
              {{ loginMode === "PASSWORD" ? "验证码登录" : "密码登录" }}
            </text>
          </view>
        </wd-form>

        <!-- #ifdef MP-WEIXIN -->
        <!-- 微信登录区域 -->
        <view v-else class="login__form">
          <view class="login__form-item">
            <button
              class="login__wx-btn"
              open-type="getPhoneNumber"
              @getphonenumber="handleWechatPhoneLogin"
            >
              <image class="login__wx-btn-icon" src="/static/icons/weixin.png" mode="aspectFit" />
              微信一键登录
            </button>
          </view>

          <!-- 其他登录方式 -->
          <view class="login__form-item login__mode-switch" @click="loginMode = 'PASSWORD'">
            <text class="login__mode-switch-text">其他登录方式</text>
            <text class="login__mode-switch-link">账号登录</text>
          </view>
        </view>
        <!-- #endif -->

        <!-- #ifdef MP-WEIXIN -->
        <!-- 分割线 -->
        <view v-if="loginMode !== 'WECHAT'" class="login__divider">
          <view class="login__divider-line" />
          <text class="login__divider-text">其他登录方式</text>
          <view class="login__divider-line" />
        </view>

        <!-- 微信登录入口 -->
        <view v-if="loginMode !== 'WECHAT'" class="login__oauth-row">
          <image
            class="login__wx-icon"
            src="/static/icons/weixin.png"
            mode="aspectFit"
            @click="loginMode = 'WECHAT'"
          />
        </view>

        <!-- 协议勾选 -->
        <view class="login__policy">
          <wd-checkbox v-model="hasAcceptedPolicy" type="square" size="32rpx">
            <text class="login__policy-text">
              我已阅读并同意
              <text class="login__policy-link" @click.stop="navigateToAgreement('user')">
                《用户协议》
              </text>
              与
              <text class="login__policy-link" @click.stop="navigateToAgreement('privacy')">
                《隐私政策》
              </text>
            </text>
          </wd-checkbox>
        </view>
        <!-- #endif -->
      </view>
    </view>

    <!-- 绑定手机号弹窗（微信静默登录用户首次使用） -->
    <bind-mobile-popup
      ref="bindMobilePopupRef"
      v-model="showBindMobilePopup"
      @success="completeLogin"
    />

    <!-- 协议确认弹窗（useDialog("policy-box") 定向挂载，不能走全局实例） -->
    <wd-dialog selector="policy-box" root-portal />
  </view>
</template>

<script lang="ts" setup>
import { onLoad } from "@dcloudio/uni-app";
import { useToast, useDialog } from "@wot-ui/ui";
import type { FormSchema } from "@wot-ui/ui/components/wd-form/types";

import { useUserStore } from "@/store/modules/user";
import { useSmsLoginCode, isValidMobile } from "@/composables/useSmsLoginCode";
import { getErrorMessage } from "@/utils/error";
import AuthAPI from "@/api/auth";
import BindMobilePopup from "./components/bind-mobile-popup.vue";

definePage({
  name: "login",
  style: { navigationStyle: "custom", navigationBarTitleText: "" },
  layout: "blank",
});

const toast = useToast();
const dialog = useDialog("policy-box");
const userStore = useUserStore();
const loginFormRef = ref();
const bindMobilePopupRef = ref<InstanceType<typeof BindMobilePopup>>();

// 表单状态
const isLoggingIn = ref(false);
const isPwdVisible = ref(false);
const hasAcceptedPolicy = ref(false);
const loginMode = ref<"PASSWORD" | "SMS" | "WECHAT">("PASSWORD");
const { countdown: smsCountdown, sendCode } = useSmsLoginCode();

const formData = ref({
  username: "admin",
  password: "123456",
  code: "123456",
  captchaCode: "",
});

// 图形验证码
const captchaId = ref("");
const captchaBase64 = ref("");
const isCaptchaLoading = ref(false);

const redirect = ref("/pages/index/index");

// 绑定手机号弹窗显隐（openid 由弹窗 open 方法传入）
const showBindMobilePopup = ref(false);

const pendingLoginAction = ref<"FORM" | "WECHAT_PHONE" | null>(null);
const pendingWechatPhoneCode = ref("");

// 计算属性
const loginModeDesc = computed(() => {
  const modeMap = {
    PASSWORD: "使用账号密码登录",
    SMS: "使用手机验证码登录",
    WECHAT: "使用微信快捷登录",
  };
  return modeMap[loginMode.value];
});

// 表单校验规则
const formSchema = computed<FormSchema>(() => ({
  validate(model) {
    const issues: { path: string[]; message: string }[] = [];
    if (loginMode.value === "PASSWORD") {
      if (!(model.username || "").trim()) {
        issues.push({ path: ["username"], message: "请输入用户名" });
      }
      if (!(model.password || "").trim()) {
        issues.push({ path: ["password"], message: "请输入密码" });
      }
      if (!(model.captchaCode || "").trim()) {
        issues.push({ path: ["captchaCode"], message: "请输入验证码" });
      }
    } else if (loginMode.value === "SMS") {
      if (!(model.username || "").trim()) {
        issues.push({ path: ["username"], message: "请输入手机号" });
      } else if (!isValidMobile(model.username)) {
        issues.push({ path: ["username"], message: "请输入正确的手机号" });
      }
      if (!(model.code || "").trim()) {
        issues.push({ path: ["code"], message: "请输入验证码" });
      }
    }
    return issues;
  },
}));

// 图形验证码
const loadCaptcha = async () => {
  if (isCaptchaLoading.value) return;
  try {
    isCaptchaLoading.value = true;
    captchaBase64.value = "";
    const res = await AuthAPI.getCaptcha();
    captchaId.value = res.captchaId;
    captchaBase64.value = res.captchaBase64;
  } catch {
    // 获取验证码失败由 API 层处理
  } finally {
    isCaptchaLoading.value = false;
  }
};

// 切换登录方式（不重置验证码冷却：同一手机号冷却期内切回仍应等待）
const toggleLoginMode = () => {
  if (loginMode.value === "PASSWORD") {
    loginMode.value = "SMS";
    formData.value.username = "18888888888";
    formData.value.password = "";
    formData.value.code = "";
  } else {
    loginMode.value = "PASSWORD";
    formData.value.username = "admin";
    formData.value.password = "123456";
    formData.value.code = "";
    formData.value.captchaCode = "";
    loadCaptcha();
  }
};

// 协议弹窗
const openPolicyDialog = (action: "FORM" | "WECHAT_PHONE", phoneCode = "") => {
  pendingLoginAction.value = action;
  pendingWechatPhoneCode.value = phoneCode;
  dialog
    .confirm({
      title: "提示",
      msg: "请阅读并同意《用户协议》与《隐私政策》",
    })
    .then(async () => {
      hasAcceptedPolicy.value = true;
      const act = pendingLoginAction.value;
      const code = pendingWechatPhoneCode.value;
      pendingLoginAction.value = null;
      pendingWechatPhoneCode.value = "";
      if (act === "WECHAT_PHONE") await doWechatPhoneLogin(code);
      else if (act === "FORM") await doFormLogin();
    })
    .catch(() => {
      pendingLoginAction.value = null;
      pendingWechatPhoneCode.value = "";
    });
};

// 表单登录
async function doFormLogin() {
  if (isLoggingIn.value) return;
  isLoggingIn.value = true;
  try {
    if (loginMode.value === "PASSWORD") {
      await userStore.loginByPassword({
        username: formData.value.username,
        password: formData.value.password,
        captchaId: captchaId.value,
        captchaCode: formData.value.captchaCode,
      });
    } else {
      await userStore.loginBySms({
        mobile: formData.value.username.trim(),
        code: formData.value.code,
      });
    }
    toast.success("登录成功");
    await completeLogin();
  } catch (error) {
    toast.error(getErrorMessage(error, "登录失败"));
    if (loginMode.value === "PASSWORD") loadCaptcha();
  } finally {
    isLoggingIn.value = false;
  }
}

const handleLogin = async () => {
  // 先校验表单必填项（内联提示，不再弹窗）
  const validateResult = await loginFormRef.value?.validate();
  if (!validateResult?.valid) {
    return;
  }
  // 再校验隐私协议
  if (!hasAcceptedPolicy.value) {
    openPolicyDialog("FORM");
    return;
  }
  await doFormLogin();
};

const handleSendCode = async () => {
  await sendCode(formData.value.username);
};

// 微信登录
/** 微信手机号快捷填充按钮回调事件 */
interface WxPhoneLoginEvent {
  detail: { code?: string };
}

const handleWechatPhoneLogin = async (e: WxPhoneLoginEvent) => {
  const phoneCode = e.detail.code;
  if (!hasAcceptedPolicy.value) {
    openPolicyDialog("WECHAT_PHONE", phoneCode);
    return;
  }
  if (!phoneCode) {
    await handleWechatSilentLogin();
    return;
  }
  await doWechatPhoneLogin(phoneCode);
};

async function doWechatPhoneLogin(phoneCode: string) {
  if (!phoneCode) {
    await handleWechatSilentLogin();
    return;
  }
  isLoggingIn.value = true;
  try {
    const { code: loginCode } = await uni.login();
    await userStore.loginByWxMaPhone({ loginCode, phoneCode });
    toast.success("登录成功");
    await completeLogin();
  } catch {
    toast.info("正在尝试其他登录方式...");
    await handleWechatSilentLogin();
  } finally {
    isLoggingIn.value = false;
  }
}

const handleWechatSilentLogin = async () => {
  isLoggingIn.value = true;
  try {
    const { code } = await uni.login();
    const result = await userStore.loginByWxMa(code);
    if (result.needBindMobile && result.openid) {
      bindMobilePopupRef.value?.open(result.openid);
      showBindMobilePopup.value = true;
    } else if (result.accessToken) {
      await completeLogin();
    }
  } catch (error) {
    toast.error(getErrorMessage(error, "微信登录失败"));
  } finally {
    isLoggingIn.value = false;
  }
};

/** 绑定手机号成功后的会话初始化与跳转 */
async function completeLogin() {
  await userStore.loadUserInfo();
  setTimeout(() => uni.reLaunch({ url: redirect.value }), 800);
}

const navigateToAgreement = (type: string) => {
  const url =
    type === "user"
      ? "/subPages/mine/settings/agreement/index"
      : "/subPages/mine/settings/privacy/index";
  uni.navigateTo({ url });
};

// 生命周期
onLoad((options) => {
  const fromQuery = options?.redirect ? decodeURIComponent(options.redirect) : "";
  if (fromQuery && fromQuery !== "/pages/login/index") redirect.value = fromQuery;
  loadCaptcha();
});
</script>

<style lang="scss" scoped>
.login {
  min-height: 100vh;
  background: linear-gradient(
    135deg,
    var(--color-bg-page) 0%,
    var(--color-bg-card) 50%,
    var(--color-primary-light) 100%
  );
}

.login__decoration {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  overflow: hidden;
  pointer-events: none;
}

.login__circle {
  position: absolute;
  filter: blur(64px);
  border-radius: 50%;

  &--1 {
    top: -160rpx;
    left: -160rpx;
    width: 480rpx;
    height: 480rpx;
    background-color: var(--color-primary-alpha-20);
  }

  &--2 {
    right: -160rpx;
    bottom: -160rpx;
    width: 640rpx;
    height: 640rpx;
    background-color: var(--color-primary-alpha-15);
  }
}

.login__body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 96rpx;
}

.login__brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 24rpx;
  margin-bottom: 32rpx;
}

.login__logo-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 20rpx;
  background: var(--color-bg-card);
  border: 1rpx solid var(--color-border);
  border-radius: 28rpx;
  box-shadow: var(--shadow-sm);
}

.login__logo {
  width: 72rpx;
  height: 72rpx;
}

.login__brand-name {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: 0.05em;
}

.login__card {
  width: 100%;
  padding: 44rpx;
  background-color: var(--color-bg-card);
  border: 2rpx solid var(--color-border-light);
  border-radius: 48rpx;
  box-shadow: var(--shadow-float);

  @supports (backdrop-filter: blur(24px)) or (-webkit-backdrop-filter: blur(24px)) {
    background-color: var(--color-bg-card-alpha-95);
    -webkit-backdrop-filter: blur(24px);
    backdrop-filter: blur(24px);
  }
}

// 卡片头部
.login__card-head {
  margin-bottom: 36rpx;
  text-align: center;
}

.login__card-title {
  font-size: 36rpx;
  font-weight: 700;
  color: var(--color-text);
}

.login__card-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 26rpx;
  color: var(--color-text-secondary);
}

.login__form-item {
  margin-top: 40rpx;

  &:first-child {
    margin-top: 0;
  }
}

// 表单行：去掉 cell 默认内边距，与按钮/分割线同宽，行距统一
.login__card :deep(.wd-form-item.wd-cell) {
  padding: 0;
  margin-top: 24rpx;
  background: transparent;

  .wd-cell__right {
    margin-top: 0;
  }

  &:first-child {
    margin-top: 0;
  }
}

// 垂直布局下隐藏左侧区域（无标题时）
:deep(.wd-form-item .wd-cell__left) {
  display: none;
}

:deep(.wd-form-item .wd-cell__wrapper) {
  flex-direction: column;
}

:deep(.wd-form-item .wd-cell__right),
:deep(.wd-form-item .wd-cell__body),
:deep(.wd-form-item .wd-cell__value) {
  width: 100%;
}

// 错误提示：独占一行，显示在输入框下方（颜色沿用 wot 默认的 danger）
.login__card :deep(.wd-form-item__error-message) {
  display: block;
  width: 100%;
  padding: 8rpx 0 0;
  font-size: 24rpx;
  line-height: 1.5;
}

// 输入框行
.login__field {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  width: 100%;
  height: 88rpx;
  padding: 0 32rpx;
  background-color: var(--color-fill-1);
  border-radius: 24rpx;
}

.login__field-input {
  flex: 1;
  min-width: 0;
  height: 100%;
  margin-left: 24rpx;
  font-size: 28rpx;
  color: var(--color-text);
}

// 密码显隐图标
.login__field-suffix {
  flex-shrink: 0;
  padding-left: 20rpx;
}

// 图形验证码图片
.login__captcha-img {
  flex-shrink: 0;
  width: 200rpx;
  height: 72rpx;
  border-radius: 12rpx;
}

.login__wx-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 88rpx;
  font-size: 32rpx;
  font-weight: 600;
  color: var(--color-text-inverse);
  background-color: var(--color-wx-green);
  border-radius: 24rpx;
  box-shadow: 0 20rpx 30rpx -6rpx rgba(34, 197, 94, 0.3);

  &:active {
    transform: scale(0.98);
  }
}

.login__wx-btn-icon {
  width: 40rpx;
  height: 40rpx;
  margin-right: 16rpx;
}

.login__code-btn {
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

.login__mode-switch {
  display: flex;
  justify-content: center;
}

.login__mode-switch-text {
  font-size: 28rpx;
  color: var(--color-text-secondary);
}

.login__mode-switch-link {
  margin-left: 8rpx;
  font-size: 28rpx;
  font-weight: 500;
  color: var(--color-primary);
}

.login__divider {
  display: flex;
  align-items: center;
  margin: 32rpx 0;
}

.login__divider-line {
  flex: 1;
  height: 2rpx;
  background-color: var(--color-border);
}

.login__divider-text {
  padding: 0 32rpx;
  font-size: 24rpx;
  color: var(--color-text-placeholder);
}

.login__oauth-row {
  display: flex;
  gap: 64rpx;
  justify-content: center;
}

.login__wx-icon {
  width: 72rpx;
  height: 72rpx;

  &:active {
    transform: scale(0.95);
  }
}

.login__policy {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 24rpx;
  margin-top: 32rpx;
  border-top: 2rpx solid var(--color-border-light);
}

.login__policy-text {
  font-size: 24rpx;
  line-height: 1.5;
  color: var(--color-text-secondary);
}

.login__policy-link {
  color: var(--color-primary);
}

.login__demo-hint {
  display: flex;
  justify-content: center;
  margin-top: 24rpx;
}

.login__demo-hint-text {
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
  .login__card {
    background-color: #252d3a;
    border-color: rgba(255, 255, 255, 0.08);
    box-shadow: 0 20rpx 50rpx -10rpx rgba(0, 0, 0, 0.4);
  }

  .login__divider-line {
    background-color: rgba(255, 255, 255, 0.12);
  }

  .login__field {
    background-color: rgba(255, 255, 255, 0.06);
  }
}
</style>
