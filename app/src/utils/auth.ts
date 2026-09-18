import { Storage } from "./storage";
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from "@/constants";

/**
 * 认证工具函数
 *
 * 使用示例：
 *
 * 1. 检查登录状态并自动跳转：
 *    if (!checkLogin()) return; // 未登录会自动跳转到登录页
 *
 * 2. 静默检查登录状态统一走 user store 的 isAuthenticated
 */

/**
 * 获取访问令牌
 * @returns 返回访问令牌，如果不存在则返回null
 */
export function getAccessToken(): string | null {
  return Storage.get<string>(ACCESS_TOKEN_KEY) || null;
}

/**
 * 设置访问令牌
 * @param token 访问令牌
 */
export function setAccessToken(token: string): void {
  Storage.set(ACCESS_TOKEN_KEY, token);
}

/**
 * 清除所有令牌
 */
export function clearTokens(): void {
  Storage.remove(ACCESS_TOKEN_KEY);
  Storage.remove(REFRESH_TOKEN_KEY);
}

function getCurrentPagePath(): string {
  const pages = getCurrentPages();
  if (pages.length === 0) return "/pages/index/index";

  const currentPage = pages[pages.length - 1];
  const route = currentPage.route || "";
  const options = (currentPage as { options?: Record<string, string> }).options || {};

  const query = Object.entries(options)
    .map(([key, value]) => `${key}=${value}`)
    .join("&");

  return query ? `/${route}?${query}` : `/${route}`;
}

/**
 * 检查用户登录状态，未登录则跳转到登录页面
 * @param silent 是否静默检查，不跳转登录页面
 * @returns 返回用户是否已登录
 */
export function checkLogin(silent: boolean = false): boolean {
  if (getAccessToken()) return true;

  if (!silent) {
    const redirect = encodeURIComponent(getCurrentPagePath());
    uni.navigateTo({
      url: `/pages/login/index?redirect=${redirect}`,
      fail: () => {
        uni.reLaunch({ url: "/pages/login/index" });
      },
    });
  }

  return false;
}
