import { defineStore } from "pinia";
import { Storage } from "@/utils/storage";
import { THEME_MODE_KEY, THEME_COLOR_KEY } from "@/constants";
import type { ConfigProviderThemeVars } from "@wot-ui/ui";

/** 主题色选项 */
export interface ThemeColorOption {
  name: string;
  value: string;
  primary: string;
}

/** 主题类型 */
export type ThemeMode = "light" | "dark";

/** 预定义的主题色选项 */
export const themeColorOptions: ThemeColorOption[] = [
  { name: "默认蓝", value: "blue", primary: "#165DFF" },
  { name: "活力橙", value: "orange", primary: "#FF7D00" },
  { name: "薄荷绿", value: "green", primary: "#07C160" },
  { name: "樱花粉", value: "pink", primary: "#FF69B4" },
  { name: "紫罗兰", value: "purple", primary: "#8A2BE2" },
  { name: "朱砂红", value: "red", primary: "#FF4757" },
];

interface ProviderThemeVars extends ConfigProviderThemeVars {
  colorTheme: string;
}

/** 主题状态管理 Store */

export const useThemeStore = defineStore("theme", () => {
  // 状态

  /** 当前主题模式 */
  const themeMode = ref<ThemeMode>(Storage.get<ThemeMode>(THEME_MODE_KEY, "light"));

  /** 已选主题色选项 */
  const selectedThemeColor = ref<ThemeColorOption>(
    Storage.get<ThemeColorOption>(THEME_COLOR_KEY, themeColorOptions[0])
  );

  /**
   * 主题变量：Wot UI v2 内置完整暗黑模式（ConfigProvider theme="dark" + 官方主题 SCSS），
   * 无需手动覆盖组件变量，这里只注入主题色
   */
  const themeVars = computed<ProviderThemeVars>(() => ({
    colorTheme: selectedThemeColor.value.primary,
  }));

  // 计算属性

  /** 是否为暗黑模式 */
  const isDark = computed(() => themeMode.value === "dark");

  // 方法

  /**
   * 按当前主题状态同步导航栏颜色
   */
  const syncNavigationBarTheme = () => {
    uni.setNavigationBarColor({
      frontColor: themeMode.value === "light" ? "#000000" : "#ffffff",
      backgroundColor: themeMode.value === "light" ? "#ffffff" : "#1f2937",
    });
  };

  /**
   * 设置主题模式
   * @param mode 目标主题模式
   */
  const setThemeMode = (mode: ThemeMode) => {
    themeMode.value = mode;
    Storage.set(THEME_MODE_KEY, mode);
    syncNavigationBarTheme();
  };

  /**
   * 在明暗两种模式间切换
   */
  const toggleThemeMode = () => {
    setThemeMode(themeMode.value === "light" ? "dark" : "light");
  };

  /**
   * 设置主题色
   * @param color 主题色选项
   */
  const setThemeColor = (color: ThemeColorOption) => {
    selectedThemeColor.value = color;
    Storage.set(THEME_COLOR_KEY, color);
  };

  /**
   * 初始化主题：同步导航栏（需等首个页面渲染完成，nextTick 保证时序）
   */
  const initTheme = () => {
    nextTick(() => {
      syncNavigationBarTheme();
    });
  };

  // 导出

  return {
    // 状态
    themeMode,
    selectedThemeColor,
    themeVars,

    // 计算属性
    isDark,

    // 方法
    setThemeMode,
    toggleThemeMode,
    setThemeColor,
    syncNavigationBarTheme,
    initTheme,
  };
});
