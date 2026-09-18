import { defineConfig, type UserConfig, type ConfigEnv, loadEnv } from "vite";
import uni from "@dcloudio/vite-plugin-uni";
import AutoImport from "unplugin-auto-import/vite";
import UniLayouts from "@uni-helper/vite-plugin-uni-layouts";
import UniPages from "@uni-helper/vite-plugin-uni-pages";

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import Components from "@uni-helper/vite-plugin-uni-components";
import type { ComponentResolver } from "@uni-helper/vite-plugin-uni-components";
import { kebabCase } from "@uni-helper/vite-plugin-uni-components";

/**
 * 自定义 Wot UI v2 组件解析器
 *
 * 由于 @wot-ui/ui v2 的包名和路径发生了变化，需要自定义 resolver
 * 官方迁移文档: https://wot-ui.cn/guide/migration-v2.html#vite-插件自动导入
 *
 * @returns ComponentResolver
 */
function WotUIResolver(): ComponentResolver {
  return {
    type: "component",
    resolve: (name: string) => {
      if (name.match(/^Wd[A-Z]/)) {
        const compName = kebabCase(name);
        return {
          name,
          from: `@wot-ui/ui/components/${compName}/${compName}.vue`,
        };
      }
    },
  };
}

export default defineConfig(async ({ mode }: ConfigEnv): Promise<UserConfig> => {
  const UnoCss = await import("unocss/vite").then((i) => i.default);
  const env = loadEnv(mode, process.cwd());
  const isProd = mode === "production";

  const pkg = JSON.parse(readFileSync(resolve(process.cwd(), "package.json"), "utf-8")) as {
    version?: string;
  };

  return {
    define: {
      "import.meta.env.VITE_APP_VERSION": JSON.stringify(pkg.version ?? ""),
    },
    server: {
      host: "0.0.0.0",
      port: +env.VITE_APP_PORT,
      open: true,
      proxy: {
        [env.VITE_APP_BASE_API]: {
          changeOrigin: true,
          target: env.VITE_APP_API_URL,
          rewrite: (path) => path.replace(new RegExp("^" + env.VITE_APP_BASE_API), ""),
        },
      },
    },
    build: {
      target: "es6",
      cssTarget: "chrome61",
      // 微信小程序单文件上传限制 2MB，生产构建关闭 sourcemap 并尽量减少调试输出
      sourcemap: false,
    },
    esbuild: isProd
      ? {
          drop: ["console", "debugger"],
        }
      : undefined,
    optimizeDeps: {
      include: ["@wot-ui/ui"],
      exclude: ["vue-demi"],
    },
    plugins: [
      // make sure put it before `Uni()`
      UnoCss(),
      UniLayouts(),
      UniPages({
        dts: "src/types/uni-pages.d.ts",
        subPackages: ["src/subPages"],
        /**
         * 排除的页面，相对于 dir 和 subPackages
         * @default []
         */
        exclude: ["**/components/**/*.*"],
      }),
      Components({
        resolvers: [WotUIResolver()],
        dirs: ["src/components"],
        dts: "src/types/components.d.ts",
      }),

      AutoImport({
        imports: [
          "vue",
          "uni-app",
          "pinia",
          {
            from: "uni-mini-router",
            imports: ["createRouter", "useRouter", "useRoute"],
          },
          {
            from: "@wot-ui/ui",
            imports: ["useToast", "useDialog", "useNotify", "CommonUtil"],
          },
        ],
        dts: "src/types/auto-imports.d.ts", // 自动生成的类型声明文件
        dirs: ["src/composables", "src/store", "src/utils", "src/api"],
        vueTemplate: true,
      }),

      uni(),
    ],
  };
});
