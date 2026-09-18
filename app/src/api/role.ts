import request from "@/utils/request";

const ROLE_BASE_URL = "/api/v1/roles";

const RoleAPI = {
  /** 获取角色分页数据 */
  getPage(queryParams?: RolePageQuery) {
    return request<PageResult<RoleItem>>({
      url: `${ROLE_BASE_URL}`,
      method: "GET",
      data: queryParams,
    });
  },

  /** 获取角色下拉数据源 */
  getOptions() {
    return request<OptionType[]>({
      url: `${ROLE_BASE_URL}/options`,
      method: "GET",
    });
  },

  /** 获取角色的菜单ID集合 */
  getMenuIds(roleId: number) {
    return request<number[]>({
      url: `${ROLE_BASE_URL}/${roleId}/menu-ids`,
      method: "GET",
    });
  },

  /** 分配菜单权限 */
  assignMenus(roleId: number, menuIds: number[]) {
    return request({
      url: `${ROLE_BASE_URL}/${roleId}/menus`,
      method: "PUT",
      data: menuIds,
    });
  },

  /** 获取角色表单数据 */
  getFormData(id: number) {
    return request<RoleForm>({
      url: `${ROLE_BASE_URL}/${id}/form`,
      method: "GET",
    });
  },

  /** 新增角色 */
  create(data: RoleForm) {
    return request({
      url: `${ROLE_BASE_URL}`,
      method: "POST",
      data: data,
    });
  },

  /** 更新角色 */
  update(id: number, data: RoleForm) {
    return request({
      url: `${ROLE_BASE_URL}/${id}`,
      method: "PUT",
      data: data,
    });
  },

  /**
   * 批量删除角色
   *
   * @param ids 角色ID，多个以英文逗号(,)分隔
   */
  deleteByIds(ids: string) {
    return request({
      url: `${ROLE_BASE_URL}/${ids}`,
      method: "DELETE",
    });
  },
};

export default RoleAPI;

/** 角色分页查询参数 */
export interface RolePageQuery extends PageQuery {
  keywords?: string;
}

/** 角色分页对象 */
export interface RoleItem {
  code?: string;
  id: number;
  name?: string;
  sort?: number;
  status?: number;
  /** 数据权限(1-所有数据 2-部门及子部门数据 3-本部门数据 4-本人数据 5-自定义部门数据) */
  dataScope?: number;
  dataScopeLabel?: string;
  createTime?: string;
  updateTime?: string;
}

/** 角色表单对象 */
export interface RoleForm {
  id?: number;
  code?: string;
  dataScope: number;
  name?: string;
  sort: number;
  /** 角色状态(1-正常；0-停用) */
  status?: number;
}
