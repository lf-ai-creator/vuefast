// src/types/env.d.ts
/**
 * 环境变量类型声明
 */
interface ImportMetaEnv {
  /**
   * 应用端口
   */
  VITE_APP_PORT: number;
  /** API基础路径 */
  readonly VITE_APP_BASE_API: string;
  /** API服务器URL */
  readonly VITE_APP_API_URL: string;

  /** 应用版本号 */
  readonly VITE_APP_VERSION: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
