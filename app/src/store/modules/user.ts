import { defineStore } from "pinia";
import AuthAPI, {
  type PasswordLoginParams,
  type SmsLoginParams,
  type WxMaPhoneLoginParams,
  type WxMaBindMobileParams,
} from "@/api/auth";
import UserAPI, { type UserInfo } from "@/api/user";
import { setAccessToken as persistAccessToken, getAccessToken, clearTokens } from "@/utils/auth";
import { Storage } from "@/utils/storage";
import { USER_INFO_KEY } from "@/constants";

/**
 * 用户状态管理 Store
 *
 * 会话约定：
 * - accessToken 是登录态的唯一事实来源（响应式），isAuthenticated 统一判断登录
 * - setAccessToken 登录成功后集中写入；resetSession 同时清理内存与持久化（退出、登录失效共用）
 */

export const useUserStore = defineStore("user", () => {
  // 状态

  /** 访问令牌（响应式会话凭据，初始化时从持久化恢复） */
  const accessToken = ref<string>(getAccessToken() || "");

  /** 用户信息 */
  const userInfo = ref<UserInfo | undefined>(Storage.get<UserInfo>(USER_INFO_KEY));

  /** 统一登录判断 */
  const isAuthenticated = computed(() => !!accessToken.value);

  /** 必填资料是否完善（昵称与头像齐备） */
  const isProfileComplete = computed(() => !!(userInfo.value?.nickname && userInfo.value?.avatar));

  // 会话管理

  /** 登录成功后的集中写入（内存 + 持久化保持同步） */
  function setAccessToken(token: string): void {
    accessToken.value = token;
    persistAccessToken(token);
  }

  /** 同时清理内存与持久化会话（退出登录、401 登录失效共用） */
  function resetSession(): void {
    accessToken.value = "";
    userInfo.value = undefined;
    clearTokens();
    Storage.remove(USER_INFO_KEY);
  }

  // 登录方法

  /**
   * 账号密码登录
   */
  const loginByPassword = async (data: PasswordLoginParams) => {
    const result = await AuthAPI.loginByPassword(data);
    setAccessToken(result.accessToken);
    return result;
  };

  /**
   * 短信验证码登录
   */
  const loginBySms = async (data: SmsLoginParams) => {
    const result = await AuthAPI.loginBySms(data);
    setAccessToken(result.accessToken);
    return result;
  };

  /**
   * 微信小程序静默登录
   */
  const loginByWxMa = async (code: string) => {
    const result = await AuthAPI.wxMaSilentLogin(code);
    if (result.accessToken) {
      setAccessToken(result.accessToken);
    }
    return result;
  };

  /**
   * 微信小程序一键登录（企业小程序）
   */
  const loginByWxMaPhone = async (data: WxMaPhoneLoginParams) => {
    const result = await AuthAPI.wxMaPhoneLogin(data);
    setAccessToken(result.accessToken);
    return result;
  };

  /**
   * 微信小程序绑定手机号
   */
  const bindMobileForWxMa = async (data: WxMaBindMobileParams) => {
    const result = await AuthAPI.wxMaBindMobile(data);
    setAccessToken(result.accessToken);
    return result;
  };

  // 用户信息方法

  /**
   * 加载当前登录用户信息（请求接口、更新响应式状态、写入存储）
   */
  const loadUserInfo = async () => {
    const data = await UserAPI.getCurrentUser();
    Storage.set(USER_INFO_KEY, data);
    userInfo.value = data;
    return data;
  };

  /**
   * 登出：远端退出 + 本地清理（内存与持久化）+ 跳转登录页（唯一导航入口）
   */
  const logout = async () => {
    try {
      await AuthAPI.logout();
    } catch {
      // 登出失败静默处理，继续清理本地状态
    } finally {
      resetSession();
      uni.reLaunch({ url: "/pages/login/index" });
    }
  };

  // 导出

  return {
    // 状态与会话
    accessToken,
    userInfo,
    isAuthenticated,
    isProfileComplete,
    setAccessToken,
    resetSession,
    // 登录
    loginByPassword,
    loginBySms,
    loginByWxMa,
    loginByWxMaPhone,
    bindMobileForWxMa,
    // 用户信息
    logout,
    loadUserInfo,
  };
});
