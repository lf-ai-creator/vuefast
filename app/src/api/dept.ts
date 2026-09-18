import request from "@/utils/request";

const DEPT_BASE_URL = "/api/v1/depts";

const DeptAPI = {
  /** 获取部门树形列表 */
  getList(queryParams?: DeptQuery) {
    return request<DeptItem[]>({
      url: `${DEPT_BASE_URL}`,
      method: "GET",
      data: queryParams,
    });
  },

  /** 获取部门下拉列表 */
  getOptions() {
    return request<OptionType[]>({
      url: `${DEPT_BASE_URL}/options`,
      method: "GET",
    });
  },

  /** 获取部门表单数据 */
  getFormData(id: number) {
    return request<DeptForm>({
      url: `${DEPT_BASE_URL}/${id}/form`,
      method: "GET",
    });
  },

  /** 新增部门 */
  create(data: DeptForm) {
    return request({
      url: `${DEPT_BASE_URL}`,
      method: "POST",
      data: data,
    });
  },

  /** 修改部门 */
  update(id: number, data: DeptForm) {
    return request({
      url: `${DEPT_BASE_URL}/${id}`,
      method: "PUT",
      data: data,
    });
  },

  /**
   * 删除部门
   *
   * @param ids 部门ID，多个以英文逗号(,)分隔
   */
  deleteByIds(ids: string) {
    return request({
      url: `${DEPT_BASE_URL}/${ids}`,
      method: "DELETE",
    });
  },
};

export default DeptAPI;

/** 部门查询参数 */
export interface DeptQuery {
  keywords?: string;
  status?: number;
}

/** 部门类型 */
export interface DeptItem {
  children?: DeptItem[];
  createTime?: Date;
  id?: number;
  name?: string;
  code?: string;
  parentId?: number;
  sort?: number;
  /** 状态(1:启用；0:禁用) */
  status?: number;
  updateTime?: Date;
}

/** 部门表单类型 */
export interface DeptForm {
  /** 部门ID(新增不填) */
  id?: number;
  name?: string;
  code?: string;
  parentId: number;
  sort: number;
  /** 状态(1:启用；0:禁用) */
  status?: number;
}
