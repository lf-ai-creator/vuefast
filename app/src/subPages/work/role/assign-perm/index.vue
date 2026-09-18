<template>
  <view class="assign-perm">
    <!-- 固定头部：搜索栏 + 操作栏 -->
    <view class="header">
      <view class="role-bar">
        <text class="role-bar__label">角色</text>
        <text class="role-bar__value">{{ roleName || "-" }}</text>
      </view>

      <view class="action-bar">
        <view class="action-bar__left">
          <wd-button type="" size="small" variant="plain" @click="handleSelectAll">全选</wd-button>
          <wd-button type="" size="small" variant="plain" @click="handleClearAll">
            取消全选
          </wd-button>
        </view>
      </view>
    </view>

    <!-- 可滚动区域：权限树 -->
    <scroll-view class="tree-container" scroll-y>
      <custom-tree
        :data="menuTree"
        :checkable="true"
        :checked-keys="checkedKeys"
        :default-expand-all="true"
        value-key="id"
        label-key="name"
        children-key="children"
        @check="handleCheck"
      >
        <template #content="{ node, checked }">
          <view class="node-content">
            <view class="node-content__info">
              <wd-icon
                v-if="node.type === 'C'"
                name="folder"
                size="18"
                :color="checked ? 'var(--color-primary)' : 'var(--color-text-secondary)'"
              />
              <wd-icon
                v-else-if="node.type === 'M'"
                name="menu"
                size="18"
                :color="checked ? 'var(--color-primary)' : 'var(--color-text-secondary)'"
              />
              <wd-icon
                v-else
                name="tag"
                size="16"
                :color="checked ? 'var(--color-primary)' : 'var(--color-text-secondary)'"
              />
              <text class="node-content__label" :class="{ 'is-checked': checked }">
                {{ node.name }}
              </text>
            </view>
            <wd-tag
              v-if="node.type"
              size="small"
              :type="node.type === 'C' ? 'primary' : node.type === 'M' ? 'success' : 'warning'"
              plain
            >
              {{ node.type === "C" ? "目录" : node.type === "M" ? "菜单" : "按钮" }}
            </wd-tag>
          </view>
        </template>
      </custom-tree>

      <wd-empty v-if="menuTree.length === 0" icon="search-line" tip="暂无菜单数据" />
    </scroll-view>

    <!-- 固定底部操作栏 -->
    <view class="bottom-bar">
      <wd-button type="info" variant="plain" @click="handleCancel">取消</wd-button>
      <wd-button :loading="isSubmitting" @click="handleSubmit">保存</wd-button>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { onLoad } from "@dcloudio/uni-app";
import MenuAPI, { type MenuItem } from "@/api/menu";
import RoleAPI from "@/api/role";
import CustomTree from "@/subPages/work/components/custom-tree.vue";
import type { TreeOption } from "@/subPages/work/components/custom-tree.vue";

definePage({
  name: "role-assign-perm",
  style: { navigationBarTitleText: "分配权限" },
  layout: "blank",
});

const toast = useToast();
const isSubmitting = ref(false);
const roleId = ref<number>(0);
const roleName = ref("");
const menuList = ref<MenuItem[]>([]);
const checkedKeys = ref<string[]>([]);

// 转换菜单为树结构
const menuTree = computed<TreeOption[]>(() => {
  if (!menuList.value.length) return [];
  return transformMenuToTree(menuList.value);
});

// 转换菜单为树组件格式
function transformMenuToTree(menus: MenuItem[]): TreeOption[] {
  return menus.map((menu) => {
    const id = String(menu.id);
    const name = menu.name ?? "";
    return {
      value: id,
      label: name,
      id,
      name,
      type: menu.type,
      children: menu.children ? transformMenuToTree(menu.children) : undefined,
    };
  });
}

// 处理选中变化
function handleCheck(keys: string[]) {
  checkedKeys.value = keys;
}

// 全选
function handleSelectAll() {
  const allIds = getAllMenuIds(menuList.value);
  checkedKeys.value = allIds;
}

// 取消全选
function handleClearAll() {
  checkedKeys.value = [];
}

// 获取所有菜单ID
function getAllMenuIds(menus: MenuItem[]): string[] {
  const ids: string[] = [];
  function traverse(list: MenuItem[]) {
    for (const menu of list) {
      if (menu.id) ids.push(String(menu.id));
      if (menu.children) traverse(menu.children);
    }
  }
  traverse(menus);
  return ids;
}

// 取消
function handleCancel() {
  uni.navigateBack();
}

// 提交
async function handleSubmit() {
  isSubmitting.value = true;
  try {
    await RoleAPI.assignMenus(roleId.value, checkedKeys.value.map(Number));
    toast.success("保存成功");
    uni.navigateBack();
  } finally {
    isSubmitting.value = false;
  }
}

// 加载数据
async function loadData() {
  try {
    // 并行加载菜单列表和角色已有权限
    const [menus, roleMenuIds, roleForm] = await Promise.all([
      MenuAPI.getList(),
      RoleAPI.getMenuIds(roleId.value),
      RoleAPI.getFormData(roleId.value),
    ]);
    menuList.value = menus;
    checkedKeys.value = roleMenuIds.map(String);
    roleName.value = roleForm?.name ?? "";
  } catch {
    toast.error("加载失败");
  }
}

onLoad((query) => {
  if (query?.id) {
    roleId.value = Number(query.id);
    loadData();
  }
});
</script>

<script lang="ts">
export default { options: { styleIsolation: "shared" } };
</script>

<style lang="scss" scoped>
.assign-perm {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--color-bg-card);
}

.header {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: space-between;
  padding: 12rpx 24rpx;
  background: var(--color-bg-card);
  border-bottom: 2rpx solid var(--color-border-light);
}

.role-bar {
  display: flex;
  gap: 16rpx;
  align-items: center;

  &__label {
    font-size: 24rpx;
    color: var(--color-text-secondary);
  }

  &__value {
    flex: 1;
    overflow: hidden;
    font-size: 28rpx;
    font-weight: 600;
    color: var(--color-text);
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.action-bar {
  &__left {
    display: flex;
    gap: 16rpx;
  }
}

.tree-container {
  flex: 1;
  height: 0; // 重要：让 flex + scroll-view 生效
  background: var(--color-bg-card);
}

.node-content {
  display: flex;
  flex: 1;
  gap: 16rpx;
  align-items: center;
  justify-content: flex-start;
  min-width: 0;

  &__info {
    display: flex;
    gap: 16rpx;
    min-width: 0;
  }

  &__label {
    overflow: hidden;
    font-size: 28rpx;
    color: var(--color-text);
    text-overflow: ellipsis;
    white-space: nowrap;

    &.is-checked {
      color: var(--color-primary);
    }
  }
}

.node-content :deep(.wd-tag) {
  margin-left: auto;
}

.bottom-bar {
  display: flex;
  flex-shrink: 0;
  gap: 24rpx;
  padding: 24rpx;
  background: var(--color-bg-card);
  box-shadow: 0 -2rpx 16rpx rgba(0, 0, 0, 0.05);
}

.bottom-bar :deep(.wd-button) {
  flex: 1;
}
</style>
