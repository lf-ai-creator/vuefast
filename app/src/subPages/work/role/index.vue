<template>
  <view>
    <view>
      <wd-search
        v-model="queryParams.keywords"
        placeholder="搜索角色名称/编码"
        hide-cancel
        @search="handleSearch"
      />
    </view>

    <!-- 角色列表 -->
    <view class="mt-16rpx">
      <wd-card v-for="item in roles" :key="item.id" @click="openRoleDialog(item.id)">
        <!-- 主信息行 -->
        <view class="flex-start">
          <view class="role-card__main">
            <view class="flex-start mt-12rpx">
              <text class="role-card__name">{{ item.name }}</text>
            </view>
            <text class="role-card__code">{{ item.code }}</text>
          </view>
          <wd-tag :type="item.status === 1 ? 'success' : 'danger'">
            {{ item.status === 1 ? "正常" : "禁用" }}
          </wd-tag>
        </view>

        <!-- 辅助信息行 -->
        <view class="role-card__meta">
          <view class="role-card__detail">
            <wd-icon name="eye" size="16" class="color-text-secondary" />
            <text class="role-card__detail-text">{{ item.dataScopeLabel }}</text>
          </view>
          <view class="role-card__detail">
            <wd-icon name="sort" size="16" class="color-text-secondary" />
            <text class="role-card__detail-text">排序: {{ item.sort }}</text>
          </view>
        </view>

        <!-- 元信息行 -->
        <view class="role-card__footer">
          <text class="item-time">{{ item.createTime }}</text>
          <view
            class="item-action"
            hover-class="item-action--hover"
            @click.stop="showRoleActions(item)"
          >
            <wd-icon name="more" size="18" class="color-text-secondary" />
          </view>
        </view>
      </wd-card>

      <wd-loadmore v-if="loadMoreState !== 'idle'" :state="loadMoreState" @reload="retry" />
      <wd-empty v-else-if="total === 0" icon="search-line" tip="暂无数据" />
    </view>

    <!-- 弹窗表单 -->
    <wd-popup
      v-model="dialog.visible"
      position="bottom"
      custom-class="popup-bottom"
      @close="closeRoleDialog"
    >
      <view class="p-4">
        <view class="popup-title">
          {{ formData.id ? "编辑角色" : "新增角色" }}
        </view>
        <wd-form ref="formRef" :model="formData" :schema="rules">
          <wd-form-item prop="name" title="角色名称" required>
            <wd-input v-model="formData.name" placeholder="请输入角色名称" />
          </wd-form-item>
          <wd-form-item prop="code" title="角色编码" required>
            <wd-input v-model="formData.code" placeholder="请输入角色编码" />
          </wd-form-item>
          <!-- 数据权限选择：触发交 wd-form-item，选择器只负责弹出 -->
          <wd-form-item
            title="数据权限"
            prop="dataScope"
            required
            is-link
            :value="dataScopeLabel"
            placeholder="请选择数据权限"
            @click="showDataScopePicker = true"
          />
          <wd-select-picker
            v-model="formData.dataScope"
            v-model:visible="showDataScopePicker"
            :columns="dataScopeOptions"
          />
          <wd-form-item prop="status" title="状态">
            <wd-switch v-model="formData.status" :active-value="1" :inactive-value="0" />
          </wd-form-item>
          <wd-form-item prop="sort" title="排序">
            <wd-input-number v-model="formData.sort" :min="0" />
          </wd-form-item>
        </wd-form>
        <view class="popup-actions">
          <wd-button type="info" variant="plain" @click="closeRoleDialog">取消</wd-button>
          <wd-button :loading="isSubmitting" @click="submitRoleForm">保存</wd-button>
        </view>
      </view>
    </wd-popup>

    <!-- 浮动新增按钮 -->
    <wd-fab
      v-if="hasPermission('sys:role:create') && !dialog.visible"
      :expandable="false"
      :gap="{ bottom: 32 }"
    >
      <template #trigger>
        <view class="work-fab-trigger" @click="openRoleDialog()">
          <wd-icon name="plus" size="20" color="var(--color-text-inverse)" />
        </view>
      </template>
    </wd-fab>

    <!-- 操作菜单 -->
    <wd-action-sheet
      v-model="actionSheetVisible"
      :actions="actionSheetActions"
      cancel-text="取消"
      @select="handleActionSelect"
    />
  </view>
</template>

<script lang="ts" setup>
import { onLoad } from "@dcloudio/uni-app";
import { toFormSchema } from "@/utils/form-schema";
import { useToast } from "@wot-ui/ui";
import { useActionSheet, type ActionMenuOption } from "@/composables/useActionSheet";
import { usePagedList } from "@/composables/usePagedList";
import RoleAPI, { type RolePageQuery, RoleItem, RoleForm } from "@/api/role";
import { hasPermission } from "@/utils/permission";

definePage({
  name: "role",
  style: { navigationBarTitleText: "角色管理", enablePullDownRefresh: true },
});

const toast = useToast();
const { actionSheetVisible, actionSheetActions, showActions, handleActionSelect, confirmAction } =
  useActionSheet();
const formRef = ref();
const isSubmitting = ref(false);

const queryParams = reactive<RolePageQuery>({ pageNum: 1, pageSize: 10, keywords: "" });
const dialog = reactive({ visible: false });

// 分页加载（触底加载 + 下拉刷新统一由 usePagedList 维护）
const {
  items: roles,
  total,
  loadMoreState,
  reload,
  retry,
} = usePagedList(RoleAPI.getPage, queryParams);

const initialFormData: RoleForm = {
  id: undefined,
  name: undefined,
  code: undefined,
  dataScope: 1,
  status: 1,
  sort: 1,
};

const formData = reactive<RoleForm>({ ...initialFormData });

// 数据权限选择器状态
const showDataScopePicker = ref(false);
const dataScopeLabel = computed(() => {
  const opt = dataScopeOptions.value.find((o) => o.value === formData.dataScope);
  return opt?.label || "";
});

const dataScopeOptions = ref<Record<string, any>[]>([
  { label: "全部数据", value: 1 },
  { label: "部门及子部门数据", value: 2 },
  { label: "本部门数据", value: 3 },
  { label: "本人数据", value: 4 },
  { label: "自定义部门数据", value: 5 },
]);

const rules = toFormSchema({
  name: [{ required: true, message: "请输入角色名称" }],
  code: [{ required: true, message: "请输入角色编码" }],
  dataScope: [{ required: true, message: "请选择数据权限" }],
});

// 搜索触发
const handleSearch = () => loadRoleList();

// 加载列表（回到第一页）
function loadRoleList() {
  reload();
}

// 打开弹窗（新增/编辑）
async function openRoleDialog(id?: number) {
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
  dialog.visible = true;
  if (id) {
    formData.id = id;
    const data = await RoleAPI.getFormData(id);
    Object.assign(formData, data, { id });
  }
}

// 提交表单
function submitRoleForm() {
  formRef.value.validate().then(({ valid }: { valid: boolean }) => {
    if (!valid) return;
    isSubmitting.value = true;
    const action = formData.id ? RoleAPI.update(formData.id, formData) : RoleAPI.create(formData);
    action
      .then(() => {
        toast.success("操作成功");
        closeRoleDialog();
        loadRoleList();
      })
      .finally(() => {
        isSubmitting.value = false;
      });
  });
}

// 关闭弹窗
function closeRoleDialog() {
  dialog.visible = false;
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
}

// 更多操作
function showRoleActions(item: RoleItem) {
  const menus: ActionMenuOption[] = [];

  if (hasPermission("sys:role:update")) {
    menus.push({ name: "编辑", handler: () => openRoleDialog(item.id) });
  }

  if (hasPermission("sys:role:assign")) {
    menus.push({ name: "分配权限", handler: () => handleAssignPerm(item.id!) });
  }

  if (hasPermission("sys:role:delete")) {
    menus.push({
      name: "删除",
      color: "var(--color-danger)",
      handler: () =>
        confirmAction({
          msg: `确定要删除角色「${item.name}」吗？`,
          action: async () => {
            await RoleAPI.deleteByIds(String(item.id));
            loadRoleList();
          },
        }),
    });
  }

  showActions(menus);
}

// 分配权限
function handleAssignPerm(id: number) {
  uni.navigateTo({
    url: "/subPages/work/role/assign-perm/index?id=" + id,
  });
}

onLoad(() => {
  loadRoleList();
});
</script>

<script lang="ts">
export default { options: { styleIsolation: "shared" } };
</script>

<style lang="scss" scoped>
.role-card__main {
  flex: 1;
}

.role-card__name {
  font-size: 32rpx;
  font-weight: 700;
}

.role-card__code {
  font-size: 24rpx;
  color: var(--color-text-secondary);
}

.role-card__meta {
  display: flex;
  gap: 24rpx;
  margin-top: 12rpx;
}

.role-card__detail {
  display: flex;
  align-items: flex-start;
  min-width: 0;
}

.role-card__detail-text {
  margin-left: 8rpx;
  font-size: 24rpx;
  color: var(--color-text-secondary);
}

.role-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16rpx;
}
</style>
