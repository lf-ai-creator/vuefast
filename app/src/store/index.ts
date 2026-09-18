import type { App } from "vue";
import { createPinia } from "pinia";

const pinia = createPinia();

// 全局注册 Pinia
export function setupPinia(app: App<Element>) {
  app.use(pinia);
}

export * from "./modules/user";
export * from "./modules/theme";
export { pinia };
