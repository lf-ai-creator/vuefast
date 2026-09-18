import { checkLogin } from "@/utils/auth";

interface NavItem {
  url?: string;
}

export function useNavigation() {
  const toast = useToast();
  const handleNavClick = (item: NavItem) => {
    if (!item.url) {
      toast.info("功能开发中");
      return;
    }

    if (!checkLogin()) return;

    if (item.url.startsWith("http://") || item.url.startsWith("https://")) {
      // #ifdef H5
      window.open(item.url, "_blank");
      // #endif
      // #ifndef H5
      uni.navigateTo({
        url: `/pages/webview/index?url=${encodeURIComponent(item.url)}`,
      });
      // #endif
      return;
    }

    uni.navigateTo({
      url: item.url,
      fail: () => {
        toast.info("页面不存在");
      },
    });
  };

  return { handleNavClick };
}
