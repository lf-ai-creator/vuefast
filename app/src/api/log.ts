import request from "@/utils/request";

const LOG_BASE_URL = "/api/v1/logs";

const LogAPI = {
  /** 获取日志分页列表 */
  getPage(queryParams?: LogPageQuery) {
    return request<PageResult<LogItem>>({
      url: `${LOG_BASE_URL}`,
      method: "GET",
      data: queryParams,
    });
  },

  /** 获取访问趋势统计 */
  getVisitTrend(queryParams: VisitTrendQuery) {
    return request<VisitTrend>({
      url: `${LOG_BASE_URL}/analytics/trend`,
      method: "GET",
      data: queryParams,
    });
  },

  /** 获取访问概览统计 */
  getVisitOverview() {
    return request<VisitOverview>({
      url: `${LOG_BASE_URL}/analytics/overview`,
      method: "GET",
    });
  },
};

export default LogAPI;

/** 日志分页查询对象 */
export interface LogPageQuery extends PageQuery {
  keywords?: string;
  createTime?: [string, string] | string;
}

/** 系统日志分页对象 */
export interface LogItem {
  id?: number;
  module?: number;
  actionType?: number;
  title?: string;
  content?: string;
  operatorId?: number;
  operatorName?: string;
  requestUri?: string;
  requestMethod?: string;
  ip?: string;
  region?: string;
  browser?: string;
  os?: string;
  /** 状态：0失败 1成功 */
  status?: number;
  errorMsg?: string;
  /** 执行时间(毫秒) */
  executionTime?: number;
  createTime?: string;
}

/** 访问趋势 */
export interface VisitTrend {
  dates: string[];
  /** 浏览量(PV) */
  pvList: number[];
  /** 访客数(UV) */
  uvList: number[];
}

/** 访问趋势查询参数 */
export interface VisitTrendQuery {
  startDate: string;
  endDate: string;
}

/** 访问统计 */
export interface VisitOverview {
  /** 今日访客数(UV) */
  todayUvCount: number;
  totalUvCount: number;
  /** 访客数同比增长率（相对于昨天同一时间段的增长率） */
  uvGrowthRate: number;
  /** 今日浏览量(PV) */
  todayPvCount: number;
  totalPvCount: number;
  /** 同比增长率（相对于昨天同一时间段的增长率） */
  pvGrowthRate: number;
}
