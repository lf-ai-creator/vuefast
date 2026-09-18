/**
 * 存储工具类
 * 提供uni-app Storage操作方法
 */

import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY, THEME_MODE_KEY, THEME_COLOR_KEY } from "@/constants";

/** 清理缓存时保留的键：登录态与主题偏好（清掉会导致下次启动退出登录、设置被重置） */
const PRESERVED_KEYS = [ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY, THEME_MODE_KEY, THEME_COLOR_KEY];

/**
 * localStorage 存储
 */
function set<T>(key: string, value: T): void {
  uni.setStorageSync(key, JSON.stringify(value));
}

function get<T>(key: string, defaultValue?: T): T {
  const value = uni.getStorageSync(key);
  if (!value) return defaultValue as T;

  try {
    return JSON.parse(value);
  } catch {
    // 如果解析失败，返回原始字符串
    return value as unknown as T;
  }
}

function remove(key: string): void {
  uni.removeStorageSync(key);
}

/** 估算字符串 UTF-8 字节数（小程序没有 Blob，不能靠它算长度） */
function byteLength(value: string): number {
  let bytes = 0;
  for (let i = 0; i < value.length; i += 1) {
    const code = value.charCodeAt(i);
    bytes += code < 0x80 ? 1 : code < 0x800 ? 2 : 3;
  }
  return bytes;
}

/** 可清理缓存的字节数：只统计登录态与主题偏好之外的键 */
function getClearableBytes(): number {
  const { keys } = uni.getStorageInfoSync();
  return keys.reduce((total, key) => {
    if (PRESERVED_KEYS.includes(key)) {
      return total;
    }
    const value = uni.getStorageSync(key);
    if (value === null || value === undefined || value === "") {
      return total;
    }
    const text = typeof value === "string" ? value : JSON.stringify(value) || "";
    return total + byteLength(text);
  }, 0);
}

/**
 * 清理业务缓存：保留登录态与主题偏好
 * 不能用 uni.clearStorage()，它会连 token 和主题一起清掉
 * @returns 清除的键数量
 */
function clearCache(): number {
  const { keys } = uni.getStorageInfoSync();
  let removed = 0;
  keys.forEach((key) => {
    if (PRESERVED_KEYS.includes(key)) {
      return;
    }
    uni.removeStorageSync(key);
    removed += 1;
  });
  return removed;
}

export const Storage = {
  set,
  get,
  remove,
  getClearableBytes,
  clearCache,
};
