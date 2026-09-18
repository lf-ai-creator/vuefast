import { pages, subPackages } from "virtual:uni-pages";
import { getAccessToken } from "@/utils/auth";
import { createRouter } from "uni-mini-router";
import { useUserStore } from "@/store";

/** virtual:uni-pages 生成的页面路由描述 */
interface PageMetaRoute {
  path: string;
  meta?: Record<string, unknown>;
  [key: string]: unknown;
}

/** 分包路由描述 */
interface SubPackageRoute {
  root: string;
  pages: PageMetaRoute[];
}

// 生成路由配置
function generateRoutes() {
  const routes = pages.map((page: PageMetaRoute) => {
    const newPath = `/${page.path}`;
    const meta = page.meta ?? undefined;
    return { ...page, path: newPath, meta };
  });

  // 处理分包路由
  if (subPackages && subPackages.length > 0) {
    subPackages.forEach((subPackage: SubPackageRoute) => {
      const subRoutes = subPackage.pages.map((page) => {
        const newPath = `/${subPackage.root}/${page.path}`;
        const meta = page.meta ?? undefined;
        return { ...page, path: newPath, meta };
      });
      routes.push(...subRoutes);
    });
  }
  return routes;
}

// 创建路由实例
const router = createRouter({
  routes: generateRoutes(),
});

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  if (to.meta && to.meta.requireAuth) {
    const token = getAccessToken();

    // 无 token：弹窗提示登录
    if (!token) {
      const redirectPath = (to.path || "/pages/index/index") as string;
      next(false);
      uni.showModal({
        title: "提示",
        content: "该功能需要登录后使用",
        confirmText: "去登录",
        cancelText: "返回",
        success: (res) => {
          if (res.confirm) {
            router.push({
              path: "/pages/login/index",
              query: { redirect: encodeURIComponent(redirectPath) },
            });
          }
        },
      });
      return;
    }

    // 有 token 但无用户信息：尝试获取
    const userStore = useUserStore();
    if (!userStore.userInfo) {
      try {
        await userStore.loadUserInfo();
      } catch {
        next(false);
        userStore.logout();
        return;
      }
    }
  }

  next();
});

export default router;
