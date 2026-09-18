import request from "@/utils/request";

const MENU_BASE_URL = "/api/v1/menus";

const MenuAPI = {
  /** 获取菜单列表 */
  getList(queryParams?: MenuQuery) {
    return request<MenuItem[]>({
      url: `${MENU_BASE_URL}`,
      method: "GET",
      data: queryParams,
    });
  },

  /** 获取菜单下拉选项 */
  getOptions(includeButton = false) {
    return request<OptionType[]>({
      url: `${MENU_BASE_URL}/options`,
      method: "GET",
      data: { includeButton },
    });
  },

  /** 获取菜单表单数据 */
  getFormData(id: string) {
    return request<MenuForm>({
      url: `${MENU_BASE_URL}/${id}/form`,
      method: "GET",
    });
  },

  /** 新增菜单 */
  create(data: MenuForm) {
    return request({
      url: `${MENU_BASE_URL}`,
      method: "POST",
      data,
    });
  },

  /** 修改菜单 */
  update(id: string, data: MenuForm) {
    return request({
      url: `${MENU_BASE_URL}/${id}`,
      method: "PUT",
      data,
    });
  },

  /**
   * 删除菜单
   *
   * @param ids 菜单ID，多个以英文逗号(,)分隔
   */
  deleteByIds(ids: string) {
    return request({
      url: `${MENU_BASE_URL}/${ids}`,
      method: "DELETE",
    });
  },
};

export default MenuAPI;

/** 菜单查询参数 */
export interface MenuQuery {
  keywords?: string;
  visible?: number;
}

/** 菜单类型 */
export interface MenuItem {
  children?: MenuItem[];
  component?: string;
  createTime?: Date;
  externalUrl?: string;
  icon?: string;
  id?: string;
  name?: string;
  parentId?: string;
  perm?: string;
  routeName?: string;
  routePath?: string;
  sort?: number;
  /** 状态(1:显示；0:隐藏) */
  visible?: number;
  /** 菜单类型(C:目录；M:菜单；B:按钮) */
  type?: string | number;
}

/** 菜单表单类型 */
export interface MenuForm {
  /** 菜单ID(新增不填) */
  id?: string;
  name?: string;
  parentId: string;
  /** 菜单类型(C:目录；M:菜单；B:按钮) */
  type: string | number;
  routeName?: string;
  routePath?: string;
  component?: string;
  perm?: string;
  externalUrl?: string;
  icon?: string;
  sort?: number;
  /** 状态(1:显示；0:隐藏) */
  visible?: number;
}
