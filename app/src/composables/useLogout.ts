import { useUserStore } from "@/store";

/** 退出登录二次确认，确认后由 userStore.logout 清理会话并跳转登录页 */
export function useLogout() {
  const userStore = useUserStore();

  // 取消不做处理，确认后交给 logout 统一收尾
  const confirmLogout = () => {
    uni.showModal({
      title: "提示",
      content: "确定要退出登录吗？",
      confirmColor: "#f53f3f",
      success: async (res) => {
        if (res.confirm) {
          await userStore.logout();
        }
      },
    });
  };

  return { confirmLogout };
}
