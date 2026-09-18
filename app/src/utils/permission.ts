import { useUserStore } from "@/store";
import { ROLE_ROOT, PERM_ALL } from "@/constants";

/**
 * 判断当前用户是否拥有指定权限点（任一命中即可，根角色或通配权限直接放行）
 */
export function hasPermission(perm: string | string[]): boolean {
  if (!perm) return false;

  const keys = Array.isArray(perm) ? perm : [perm];
  if (keys.length === 0) return false;

  const userInfo = useUserStore().userInfo;
  if (!userInfo) return false;

  const { roles = [], perms = [] } = userInfo;
  if (roles.includes(ROLE_ROOT) || perms.includes(PERM_ALL)) return true;
  if (perms.length === 0) return false;

  return keys.some((key) => perms.includes(key));
}
