import { ref, computed, type Ref, type ComputedRef } from "vue";

/**
 * 微信小程序导航栏高度计算
 *
 * 参考 uni-ui 官方实现：https://github.com/dcloudio/uni-ui
 *
 * 重要说明：
 * 1. CSS 变量 --status-bar-height 在某些情况下不准确（小程序端固定 25px）
 * 2. 使用 uni.getWindowInfo().statusBarHeight 动态获取
 * 3. 微信小程序需要考虑胶囊按钮位置
 * 4. H5 没有状态栏，statusBarHeight 为 0
 *
 * 导航栏结构：
 * ┌─────────────────────────────┐
 * │        状态栏区域            │  statusBarHeight
 * ├─────────────────────────────┤
 * │    上边距                    │  menu.top - statusBarHeight
 * ├─────────────────────────────┤
 * │        胶囊按钮              │  menu.height
 * ├─────────────────────────────┤
 * │    下边距（与上边距相等）     │
 * └─────────────────────────────┘
 *
 * 导航栏高度计算公式（uni-ui 官方）：
 * navBarHeight = menu.height + (menu.top - statusBarHeight) * 2
 * totalHeight = statusBarHeight + navBarHeight
 */

interface MenuButtonRect {
  width: number;
  height: number;
  top: number;
  right: number;
  bottom: number;
  left: number;
}

export interface UseNavbarOptions {
  /** 导航栏内容高度，默认 44 */
  navBarHeight?: number;
  /** 是否有 TabBar，默认 false */
  hasTabbar?: boolean;
}

export interface UseNavbarReturn {
  // 高度信息
  statusBarHeight: Ref<number>;
  navBarHeight: number;
  totalHeight: ComputedRef<number>;
  contentPaddingTop: ComputedRef<string>;
  safeAreaBottom: Ref<number>;

  // 胶囊按钮信息
  menuButton: Ref<MenuButtonRect | null>;
  menuButtonRightGap: ComputedRef<number>;
  menuButtonLeft: ComputedRef<number>;
  menuButtonWidth: ComputedRef<number>;
  contentWidth: ComputedRef<number>;

  // 平台信息
  platform: Ref<string>;
  windowWidth: Ref<number>;

  // 方法
  init: () => void;
}

/**
 * 导航栏高度计算 Hook
 *
 * @param options 配置选项
 */
export function useNavbar(options: UseNavbarOptions = {}): UseNavbarReturn {
  const { navBarHeight = 44 } = options;

  // 状态栏高度
  const statusBarHeight = ref(0);
  // 胶囊按钮信息
  const menuButton = ref<MenuButtonRect | null>(null);
  // 安全区域底部高度
  const safeAreaBottom = ref(0);
  // 窗口宽度
  const windowWidth = ref(375);
  // 平台标识
  const platform = ref("");

  // 计算导航栏总高度（参考 uni-ui 官方实现）
  const totalHeight = computed(() => {
    // #ifdef MP-WEIXIN
    // 微信小程序：使用胶囊按钮精确计算
    if (menuButton.value && menuButton.value.height > 0 && menuButton.value.top > 0) {
      const { top, height } = menuButton.value;
      // 导航栏高度 = 胶囊按钮高度 + 上下边距
      // 上下边距 = (胶囊按钮top - 状态栏高度) * 2
      const spaceHeight = top - statusBarHeight.value;
      return statusBarHeight.value + height + spaceHeight * 2;
    }
    // #endif

    // H5 / App：状态栏高度 + 导航栏高度
    return statusBarHeight.value + navBarHeight;
  });

  // 页面内容区域的 paddingTop（用于避开固定导航栏）
  const contentPaddingTop = computed(() => `${totalHeight.value}px`);

  // 胶囊按钮右侧距离屏幕右边的距离（用于避开胶囊按钮）
  const menuButtonRightGap = computed(() => {
    // #ifdef MP-WEIXIN
    if (menuButton.value && menuButton.value.right > 0) {
      return windowWidth.value - menuButton.value.right;
    }
    // #endif
    // H5 / App 不需要避让胶囊
    return 10;
  });

  // 胶囊按钮左侧距离屏幕左边的距离
  const menuButtonLeft = computed(() => {
    // #ifdef MP-WEIXIN
    if (menuButton.value) {
      return menuButton.value.left;
    }
    // #endif
    return 0;
  });

  // 胶囊按钮宽度
  const menuButtonWidth = computed(() => {
    // #ifdef MP-WEIXIN
    if (menuButton.value) {
      return menuButton.value.width;
    }
    // #endif
    return 0;
  });

  // 页面内容区域可用宽度（避开胶囊按钮）
  const contentWidth = computed(() => {
    // #ifdef MP-WEIXIN
    if (menuButton.value) {
      // 内容区域宽度 = 胶囊按钮左侧距离 - 间距
      const gap = menuButtonRightGap.value;
      return menuButton.value.left - gap;
    }
    // #endif
    return windowWidth.value;
  });

  // #ifdef MP-WEIXIN
  const isValidMenuButtonRect = (rect: ReturnType<typeof uni.getMenuButtonBoundingClientRect>) => {
    return !!rect && rect.width > 0 && rect.height > 0 && rect.top > 0 && rect.right > 0;
  };

  const setMenuButtonRectWithRetry = (maxRetry = 6, delayMs = 50) => {
    // 兜底：合理的默认胶囊按钮尺寸，避免导航栏高度为 0
    const applyDefaultMenuButton = () => {
      menuButton.value = {
        width: 87,
        height: 32,
        top: statusBarHeight.value + 6,
        right: windowWidth.value - 10,
        bottom: statusBarHeight.value + 38,
        left: windowWidth.value - 97,
      };
    };

    try {
      const rect = uni.getMenuButtonBoundingClientRect();

      if (isValidMenuButtonRect(rect)) {
        menuButton.value = {
          width: rect.width,
          height: rect.height,
          top: rect.top,
          right: rect.right,
          bottom: rect.bottom,
          left: rect.left,
        };
        return;
      }

      if (maxRetry > 0) {
        setTimeout(() => {
          setMenuButtonRectWithRetry(maxRetry - 1, delayMs);
        }, delayMs);
      } else {
        applyDefaultMenuButton();
      }
    } catch {
      applyDefaultMenuButton();
    }
  };
  // #endif

  // 初始化
  const init = () => {
    try {
      const windowInfo =
        typeof uni.getWindowInfo === "function" ? uni.getWindowInfo() : uni.getSystemInfoSync();
      const deviceInfo =
        typeof uni.getDeviceInfo === "function" ? uni.getDeviceInfo() : uni.getSystemInfoSync();

      statusBarHeight.value = windowInfo.statusBarHeight || 0;
      safeAreaBottom.value = windowInfo.safeAreaInsets?.bottom || 0;
      windowWidth.value = windowInfo.windowWidth || 375;
      platform.value = deviceInfo.platform || "";

      // #ifdef MP-WEIXIN
      // 微信小程序：获取胶囊按钮位置
      setMenuButtonRectWithRetry();
      // #endif
    } catch {
      // 各字段已有声明处默认值兜底
    }
  };

  // setup 阶段同步调用，避免首次渲染闪烁
  init();

  return {
    // 高度信息
    statusBarHeight,
    navBarHeight,
    totalHeight,
    contentPaddingTop,
    safeAreaBottom,

    // 胶囊按钮信息
    menuButton,
    menuButtonRightGap,
    menuButtonLeft,
    menuButtonWidth,
    contentWidth,

    // 平台信息
    platform,
    windowWidth,

    // 方法
    init,
  };
}
