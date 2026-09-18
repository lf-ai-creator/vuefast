import request from "@/utils/request";

const USER_BASE_URL = "/api/v1/users";

const UserAPI = {
  /** 获取当前登录用户信息 */
  getCurrentUser(): Promise<UserInfo> {
    return request<UserInfo>({
      url: `${USER_BASE_URL}/me`,
      method: "GET",
    });
  },

  /** 获取用户分页列表 */
  getPage(queryParams: UserPageQuery) {
    return request<PageResult<UserItem>>({
      url: `${USER_BASE_URL}`,
      method: "GET",
      data: queryParams,
    });
  },

  /** 新增用户 */
  create(data: UserForm) {
    return request({
      url: `${USER_BASE_URL}`,
      method: "POST",
      data: data,
    });
  },

  /** 获取用户表单数据 */
  getFormData(userId: number) {
    return request<UserForm>({
      url: `${USER_BASE_URL}/${userId}/form`,
      method: "GET",
    });
  },

  /** 修改用户 */
  update(id: number, data: UserForm) {
    return request({
      url: `${USER_BASE_URL}/${id}`,
      method: "PUT",
      data: data,
    });
  },

  /** 获取个人中心用户信息 */
  getProfile() {
    return request<UserProfile>({
      url: `${USER_BASE_URL}/profile`,
      method: "GET",
    });
  },

  /** 修改个人中心用户信息 */
  updateProfile(data: UserProfileForm) {
    return request({
      url: `${USER_BASE_URL}/profile`,
      method: "PUT",
      data: data,
    });
  },

  /** 修改个人中心用户密码 */
  changePassword(data: PasswordChangeForm) {
    return request({
      url: `${USER_BASE_URL}/password`,
      method: "PUT",
      data: data,
    });
  },

  /** 解绑第三方账号 */
  unbindSocial(platform: string) {
    return request({
      url: `${USER_BASE_URL}/social?platform=${encodeURIComponent(platform)}`,
      method: "DELETE",
    });
  },

  /**
   * 发送手机/邮箱验证码
   *
   * @param contact 联系方式(手机号/邮箱)
   * @param contactType 联系方式类型(MOBILE:手机;EMAIL:邮箱)
   */
  sendVerificationCode(contact: string, contactType: string) {
    return request({
      url: `${USER_BASE_URL}/send-verification-code?contact=${encodeURIComponent(contact)}&contactType=${encodeURIComponent(contactType)}`,
      method: "POST",
    });
  },

  /** 绑定个人中心用户手机 */
  bindMobile(data: MobileBindingForm) {
    return request({
      url: `${USER_BASE_URL}/mobile`,
      method: "PUT",
      data: data,
    });
  },

  /** 绑定个人中心用户邮箱 */
  bindEmail(data: EmailBindingForm) {
    return request({
      url: `${USER_BASE_URL}/email`,
      method: "PUT",
      data: data,
    });
  },

  /**
   * 批量删除用户
   *
   * @param ids 用户ID，多个以英文逗号(,)分隔
   */
  deleteByIds(ids: string) {
    return request({
      url: `${USER_BASE_URL}/${ids}`,
      method: "DELETE",
    });
  },

  /** 重置用户密码 */
  resetPassword(userId: number | string, password: string) {
    return request({
      url: `${USER_BASE_URL}/${userId}/password/reset`,
      method: "PUT",
      data: { password },
    });
  },
};
export default UserAPI;

interface BaseUser {
  username?: string;
  nickname?: string;
  avatar?: string;
  gender?: number;
  mobile?: string;
  email?: string;
  deptName?: string;
}

/** 登录用户信息 */
export interface UserInfo extends BaseUser {
  userId?: number;
  roles?: string[];
  perms?: string[];
  /** 角色名称（前端计算字段，取 roles[0] 的中文映射） */
  roleName?: string;
}

/** 用户分页查询对象 */
export interface UserPageQuery extends PageQuery {
  keywords?: string;
  status?: number;
  deptId?: number;
  createTime?: [string, string] | string;
  field?: string;
  /** 排序方式(asc:正序,desc:倒序) */
  direction?: string;
}

/** 用户分页对象 */
export interface UserItem {
  avatar?: string;
  createTime?: string;
  deptName?: string;
  email?: string;
  gender?: number;
  id: number;
  mobile?: string;
  nickname?: string;
  /** 角色名称，多个使用英文逗号(,)分割 */
  roleNames?: string;
  /** 用户状态(1:启用;0:禁用) */
  status?: number;
  username?: string;
}

/** 个人中心用户信息 */
export interface UserProfile extends BaseUser {
  id?: number;
  /** 角色名称，多个使用英文逗号(,)分割 */
  roleNames?: string;
  createTime?: string;
}

/** 个人中心用户信息表单 */
export interface UserProfileForm extends Pick<
  BaseUser,
  "username" | "nickname" | "avatar" | "gender" | "mobile" | "email"
> {
  id?: number;
}

/** 修改密码表单 */
export interface PasswordChangeForm {
  oldPassword?: string;
  newPassword?: string;
  confirmPassword?: string;
}

/** 修改手机表单 */
export interface MobileBindingForm {
  mobile?: string;
  code?: string;
}

/** 修改邮箱表单 */
export interface EmailBindingForm {
  email?: string;
  code?: string;
}

/** 用户表单 */
export interface UserForm {
  avatar?: string;
  deptId?: number;
  email?: string;
  gender?: number;
  id?: number;
  mobile?: string;
  nickname?: string;
  /** 角色ID集合（后端 Long 序列化为字符串，兼容数字） */
  roleIds: (number | string)[];
  /** 用户状态(1:正常;0:禁用) */
  status?: number;
  username?: string;
}
