import {
  useThemeStore,
  themeColorOptions,
  type ThemeColorOption,
  type ThemeMode,
} from "@/store/modules/theme";

export function useTheme() {
  const store = useThemeStore();

  /**
   * 设置主题模式
   * @param mode 目标主题模式
   */
  function setThemeMode(mode: ThemeMode) {
    store.setThemeMode(mode);
  }

  /**
   * 在明暗两种模式间切换
   */
  function toggleThemeMode() {
    store.toggleThemeMode();
  }

  /**
   * 设置主题色
   * @param option 主题色选项
   */
  function setThemeColor(option: ThemeColorOption) {
    store.setThemeColor(option);
  }

  /**
   * 初始化主题
   */
  function initTheme() {
    store.initTheme();
  }

  // 全局主题初始化已在 App.vue onLaunch 中完成（导航栏颜色同步），
  // 组件中一般无需再调用 initTheme()

  return {
    themeMode: computed(() => store.themeMode),
    isDark: computed(() => store.isDark),
    selectedThemeColor: computed(() => store.selectedThemeColor),
    themeVars: store.themeVars,

    themeColorOptions,

    initTheme,
    setThemeMode,
    toggleThemeMode,
    setThemeColor,
  };
}

export type { ThemeColorOption, ThemeMode };
