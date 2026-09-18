import request from "@/utils/request";

const NOTICE_BASE_URL = "/api/v1/notices";

const NoticeAPI = {
  /** 获取通知公告分页数据 */
  getPage(queryParams?: NoticePageQuery) {
    return request<PageResult<NoticeItem>>({
      url: `${NOTICE_BASE_URL}`,
      method: "GET",
      data: queryParams,
    });
  },

  /** 获取通知公告表单数据 */
  getFormData(id: number) {
    return request<NoticeForm>({
      url: `${NOTICE_BASE_URL}/${id}/form`,
      method: "GET",
    });
  },

  /** 新增通知公告 */
  create(data: NoticeForm) {
    return request({
      url: `${NOTICE_BASE_URL}`,
      method: "POST",
      data: data,
    });
  },

  /** 更新通知公告 */
  update(id: number, data: NoticeForm) {
    return request({
      url: `${NOTICE_BASE_URL}/${id}`,
      method: "PUT",
      data: data,
    });
  },

  /**
   * 批量删除通知公告
   *
   * @param ids 通知公告ID，多个以英文逗号(,)分隔
   */
  deleteByIds(ids: string) {
    return request({
      url: `${NOTICE_BASE_URL}/${ids}`,
      method: "DELETE",
    });
  },

  /** 发布通知 */
  publish(id: number) {
    return request({
      url: `${NOTICE_BASE_URL}/${id}/publish`,
      method: "PUT",
    });
  },

  /** 撤回通知 */
  revoke(id: number) {
    return request({
      url: `${NOTICE_BASE_URL}/${id}/revoke`,
      method: "PUT",
    });
  },

  /** 查看通知详情 */
  getDetail(id: string) {
    return request<NoticeDetail>({
      url: `${NOTICE_BASE_URL}/${id}/detail`,
      method: "GET",
    });
  },

  /** 获取我的通知分页列表 */
  getMyNoticePage(queryParams?: NoticePageQuery) {
    return request<PageResult<NoticeItem>>({
      url: `${NOTICE_BASE_URL}/my`,
      method: "GET",
      data: queryParams,
    });
  },
};

export default NoticeAPI;

/** 通知公告分页查询参数 */
export interface NoticePageQuery extends PageQuery {
  title?: string;
  /** 发布状态(0：未发布，1：已发布，-1：已撤回) */
  publishStatus?: number;

  isRead?: number;
}

/** 通知公告表单对象 */
export interface NoticeForm {
  id?: number;
  title?: string;
  content?: string;
  /** 通知类型 */
  type?: number;
  /** 优先级(L：低，M：中，H：高) */
  level?: string;
  /** 目标类型(1-全体 2-指定) */
  targetType?: number;
  /** 目标ID合集，以,分割 */
  targetUserIds?: string;
}

/** 通知公告分页对象 */
export interface NoticeItem {
  id: string;
  title?: string;
  content?: string;
  /** 通知类型 */
  type?: number;
  publisherName?: string;
  /** 优先级(0-低 1-中 2-高) */
  priority?: number;
  /** 目标类型(0-全体 1-指定) */
  targetType?: number;
  /** 发布状态(0-未发布 1已发布 2已撤回) */
  publishStatus?: number;
  publishTime?: Date;
  revokeTime?: Date;
  /** 优先级(L-低 M-中 H-高) */
  level?: string | number;
}

export interface NoticeDetail {
  id?: string;
  title?: string;
  content?: string;
  /** 通知类型 */
  type?: number;
  publisherName?: string;
  /** 优先级(L-低 M-中 H-高) */
  level?: string;
  publishTime?: Date;
  /** 发布状态(0-未发布 1-已发布 2-已撤回) */
  publishStatus?: number;
}
