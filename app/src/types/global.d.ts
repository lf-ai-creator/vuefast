// 全局类型声明文件
// 自动引入 virtual 模块类型

/// <reference types="@uni-helper/vite-plugin-uni-pages/client" />
/// <reference types="@dcloudio/types" />
/// <reference types="@uni-helper/uni-types" />

// 如果需要其他 virtual 模块类型，可以在这里添加
// 例如：/// <reference types="xxx/client" />

declare global {
  /**
   * 微信小程序全局对象。
   *
   * 条件编译内的 `wx` 在微信端运行时存在，但 vue-tsc 仍会解析源码，
   * 因此这里提供最小声明，避免页面直接报未定义。
   */
  const wx: {
    request(options: UniApp.RequestOptions): void;
  };

  /**
   * 分页查询参数
   */
  interface PageQuery {
    pageNum: number;
    pageSize: number;
  }

  /**
   * 分页响应对象
   */
  interface PageResult<T> {
    /** 数据列表 */
    list: T[];
    /** 总数 */
    total: number;
  }

  /**
   * 组件数据源
   */
  interface OptionType {
    /** 值 */
    value: string | number;
    /** 文本 */
    label: string;
    /** 子列表  */
    children?: OptionType[];
  }

  /**
   * 响应数据
   */
  interface ApiResponse<T = any> {
    code: string;
    data: T;
    msg: string;
  }
}

export {};
