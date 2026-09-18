// 扩展 uni-mini-router 路由类型，支持从 pages.json 注入的 meta 字段
// 该声明文件会被 ts 自动合并到库类型中

import "uni-mini-router";

declare module "uni-mini-router" {
  /** 自定义路由元信息类型，可按需扩展 */
  interface RouteMeta {
    /** 是否需要登录 */
    requireAuth?: boolean;
    /** 其他自定义字段 */
    [key: string]: any;
  }

  interface Route {
    /** 来自 pages.json 的 meta 字段（动态生成时透传） */
    meta?: RouteMeta;
  }
}

export {};
