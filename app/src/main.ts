import { createSSRApp } from "vue";
import App from "./App.vue";

import "uno.css";
import "@/styles/index.scss";

import { setupPinia, useUserStore } from "@/store";
import { setUnauthorizedHandler } from "@/utils/request";
import router from "./router";

export function createApp() {
  const app = createSSRApp(App);

  setupPinia(app);
  // 注册会话失效回调：401 时由 store 统一清理内存与持久化登录态
  setUnauthorizedHandler(() => useUserStore().resetSession());
  app.use(router);

  return {
    app,
  };
}
