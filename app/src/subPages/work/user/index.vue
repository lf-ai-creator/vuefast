<template>
  <view>
    <view>
      <wd-search
        v-model="queryParams.keywords"
        placeholder="搜索用户名/手机号"
        hide-cancel
        @search="handleSearch"
      />
    </view>

    <!-- 排序筛选：搜索框→筛选 12rpx -->
    <view class="filter-bar" @click="closeOutside">
      <view class="flex-1">
        <wd-drop-menu>
          <wd-drop-menu-item
            v-model="sortValue"
            title="排序"
            :options="sortOptions"
            @change="handleSortChange"
          />
        </wd-drop-menu>
      </view>
      <wd-divider vertical />
      <view class="flex-1">
        <wd-drop-menu>
          <wd-drop-menu-item title="筛选">
            <view class="p-4">
              <wd-input
                v-model="queryParams.keywords"
                label="关键字"
                placeholder="用户名/昵称/手机号"
              />
              <wd-cell
                title="创建时间"
                :value="createTimeLabel"
                placeholder="请选择时间范围"
                is-link
                @click="showCreateTimePicker = true"
              />
              <wd-calendar
                v-model="createTimeRange"
                v-model:visible="showCreateTimePicker"
                type="daterange"
                allow-same-day
              />
              <view class="popup-actions">
                <wd-button type="info" variant="plain" @click="resetUserFilter">重置</wd-button>
                <wd-button @click="applyUserFilter">查询</wd-button>
              </view>
            </view>
          </wd-drop-menu-item>
        </wd-drop-menu>
      </view>
    </view>

    <!-- 用户列表：筛选→列表 16rpx -->
    <view class="mt-16rpx">
      <wd-card v-for="item in users" :key="item.id" @click="openUserDialog(item)">
        <!-- 主信息行：头像 + 昵称/角色部门 + 状态 -->
        <view class="user-card__header">
          <image class="user-card__avatar" :src="item.avatar" mode="aspectFill" lazy-load />
          <view class="user-card__main">
            <view class="user-card__name-row">
              <text class="user-card__name">{{ item.nickname }}</text>
              <wd-icon
                v-if="item.gender === 1"
                name="man"
                color="var(--color-primary)"
                class="ml-8rpx"
              />
              <wd-icon
                v-else-if="item.gender === 2"
                name="woman"
                color="var(--color-danger)"
                class="ml-8rpx"
              />
            </view>
            <text class="user-card__role">{{ item.roleNames }} · {{ item.deptName }}</text>
          </view>
          <wd-tag :type="item.status === 1 ? 'success' : 'danger'">
            {{ item.status === 1 ? "正常" : "禁用" }}
          </wd-tag>
        </view>

        <!-- 联系方式 -->
        <view class="user-card__contacts">
          <view v-if="item.mobile" class="user-card__contact">
            <wd-icon name="mobile" size="16" class="color-text-secondary" />
            <text class="user-card__contact-text">{{ item.mobile }}</text>
          </view>
          <view v-if="item.email" class="user-card__contact">
            <wd-icon name="email" size="16" class="color-text-secondary" />
            <text class="user-card__contact-text">{{ item.email }}</text>
          </view>
        </view>

        <!-- 创建时间 + 更多操作 -->
        <view class="user-card__footer">
          <text class="item-time">{{ formatDateTime(item.createTime) }}</text>
          <view
            class="item-action"
            hover-class="item-action--hover"
            @click.stop="showUserActions(item)"
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
      @close="closeUserDialog"
    >
      <view class="p-4">
        <view class="popup-title">
          {{ formData.id ? "编辑用户" : "新增用户" }}
        </view>
        <wd-form ref="formRef" :model="formData" :schema="rules">
          <wd-form-item prop="username" title="用户名" required>
            <wd-input
              v-model="formData.username"
              placeholder="请输入用户名"
              :readonly="!!formData.id"
            />
          </wd-form-item>
          <wd-form-item prop="nickname" title="昵称" required>
            <wd-input v-model="formData.nickname" placeholder="请输入昵称" />
          </wd-form-item>
          <!-- 部门选择：触发交 wd-form-item，选择器只负责弹出 -->
          <wd-form-item
            title="部门"
            prop="deptId"
            required
            is-link
            :value="deptLabel"
            placeholder="请选择部门"
            @click="showDeptPicker = true"
          />
          <wd-cascader
            v-model="deptSelected"
            v-model:visible="showDeptPicker"
            :options="deptOptions"
            text-key="label"
            @confirm="handleDeptConfirm"
          />

          <!-- 角色选择：触发交 wd-form-item，选择器只负责弹出 -->
          <wd-form-item
            title="角色"
            prop="roleIds"
            required
            is-link
            :value="roleLabel"
            placeholder="请选择角色"
            @click="showRolePicker = true"
          />
          <wd-select-picker
            v-model="formData.roleIds"
            v-model:visible="showRolePicker"
            :columns="roleOptions"
            @confirm="handleRoleConfirm"
          />
          <wd-form-item prop="mobile" title="手机号">
            <wd-input v-model="formData.mobile" placeholder="请输入手机号" />
          </wd-form-item>
          <wd-form-item prop="email" title="邮箱">
            <wd-input v-model="formData.email" placeholder="请输入邮箱" />
          </wd-form-item>
          <wd-form-item prop="status" title="状态">
            <wd-switch v-model="formData.status" :active-value="1" :inactive-value="0" />
          </wd-form-item>
        </wd-form>
        <view class="popup-actions">
          <wd-button type="info" variant="plain" @click="closeUserDialog">取消</wd-button>
          <wd-button :loading="isSubmitting" @click="handleUserSubmit">保存</wd-button>
        </view>
      </view>
    </wd-popup>

    <!-- 浮动新增按钮 -->
    <wd-fab
      v-if="
        hasPermission('sys:user:create') &&
        !dialog.visible &&
        !resetPwdDialog.visible &&
        !actionSheetVisible
      "
      :expandable="false"
      :gap="{ bottom: 32 }"
    >
      <template #trigger>
        <view class="work-fab-trigger" @click="openUserDialog()">
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

    <!-- 重置密码弹窗 -->
    <wd-popup v-model="resetPwdDialog.visible" position="bottom" custom-class="popup-bottom">
      <view class="p-4">
        <view class="popup-title">重置密码</view>
        <wd-form ref="resetPwdFormRef" :model="resetPwdForm" :schema="resetPwdRules">
          <wd-form-item prop="password" title="新密码" required>
            <wd-input v-model="resetPwdForm.password" placeholder="请输入新密码（至少6位）" />
          </wd-form-item>
        </wd-form>
        <view class="popup-actions">
          <wd-button type="info" variant="plain" @click="resetPwdDialog.visible = false">
            取消
          </wd-button>
          <wd-button :loading="resetPwdDialog.isSubmitting" @click="handleResetPassword">
            确认
          </wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script lang="ts" setup>
import { onLoad } from "@dcloudio/uni-app";
import dayjs from "dayjs";
import type { CascaderOption } from "@wot-ui/ui/components/wd-cascader/types";
import { toFormSchema } from "@/utils/form-schema";
import { findOptionChain } from "@/utils/tree";
import { formatDateTime } from "@/utils/format";
import { useQueue, useToast } from "@wot-ui/ui";
import { useActionSheet, type ActionMenuOption } from "@/composables/useActionSheet";
import { usePagedList } from "@/composables/usePagedList";
import UserAPI, { type UserPageQuery, UserItem, UserForm } from "@/api/user";
import RoleAPI from "@/api/role";
import DeptAPI from "@/api/dept";
import { hasPermission } from "@/utils/permission";

definePage({
  name: "user",
  style: { navigationBarTitleText: "用户管理", enablePullDownRefresh: true },
});

const toast = useToast();
const { closeOutside } = useQueue();
const { actionSheetVisible, actionSheetActions, showActions, handleActionSelect, confirmAction } =
  useActionSheet();
const formRef = ref();
const isSubmitting = ref(false);

const sortValue = ref(0);
const sortOptions = ref([
  { label: "默认排序", value: 0 },
  { label: "最近创建", value: 1 },
  { label: "最近更新", value: 2 },
]);

const queryParams = reactive<UserPageQuery>({ pageNum: 1, pageSize: 10, keywords: "" });
const dialog = reactive({ visible: false });

// 创建时间筛选：日历弹层只维护时间戳，点击「查询」时才写入查询参数
const showCreateTimePicker = ref(false);
const createTimeRange = ref<number[]>([]);
const formatDay = (ts: number) => dayjs(ts).format("YYYY-MM-DD");
const createTimeLabel = computed(() =>
  createTimeRange.value.length === 2 ? createTimeRange.value.map(formatDay).join(" ~ ") : ""
);

const initialFormData: UserForm = {
  id: undefined,
  roleIds: [],
  username: undefined,
  nickname: undefined,
  deptId: undefined,
  mobile: undefined,
  email: undefined,
  status: 1,
};

const formData = reactive<UserForm>({ ...initialFormData });
const roleOptions = ref<OptionType[]>([]);
const deptOptions = ref<OptionType[]>([]);

// 部门选择器状态
const showDeptPicker = ref(false);
const deptSelected = ref<string | number>("");
const deptLabel = ref("");

// 角色选择器状态
const showRolePicker = ref(false);
const roleLabel = ref("");

// 部门确认选择
const handleDeptConfirm = ({
  value,
  selectedOptions,
}: {
  value: string | number;
  selectedOptions: CascaderOption[];
}) => {
  formData.deptId = Number(value);
  deptLabel.value = selectedOptions.map((item) => String(item.label ?? "")).join("/");
};

// 角色确认选择
const handleRoleConfirm = ({
  selectedItems,
}: {
  value: (string | number)[];
  selectedItems: OptionType[];
}) => {
  roleLabel.value = selectedItems.map((item) => item.label).join("、");
};

const rules = toFormSchema({
  username: [{ required: true, message: "请输入用户名" }],
  nickname: [{ required: true, message: "请输入昵称" }],
  roleIds: [{ required: true, message: "请选择角色" }],
  deptId: [{ required: true, message: "请选择部门" }],
});

// 排序切换
const handleSortChange = ({ value }: { value: string | number }) => {
  const num = Number(value);
  if (num === 1) {
    queryParams.field = "create_time";
    queryParams.direction = "desc";
  } else if (num === 2) {
    queryParams.field = "update_time";
    queryParams.direction = "desc";
  } else {
    queryParams.field = "";
    queryParams.direction = "";
  }
  loadUserList();
};

// 搜索触发
const handleSearch = () => loadUserList();

// 分页加载（触底加载 + 下拉刷新统一由 usePagedList 维护）
const {
  items: users,
  total,
  loadMoreState,
  reload,
  retry,
} = usePagedList(UserAPI.getPage, queryParams);

// 加载列表（回到第一页）
function loadUserList() {
  reload();
}
// 应用筛选并刷新
function applyUserFilter() {
  if (createTimeRange.value.length === 2) {
    queryParams.createTime = createTimeRange.value.map(formatDay).join(",");
  } else {
    delete queryParams.createTime;
  }
  closeOutside();
  loadUserList();
}
// 重置筛选并刷新
function resetUserFilter() {
  queryParams.keywords = "";
  createTimeRange.value = [];
  queryParams.field = "";
  queryParams.direction = "";
  sortValue.value = 0;
  applyUserFilter();
}

// 打开弹窗（新增/编辑）
async function openUserDialog(user?: UserItem) {
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
  deptSelected.value = "";
  deptLabel.value = "";
  roleLabel.value = "";
  dialog.visible = true;
  roleOptions.value = await RoleAPI.getOptions();
  const deptData = await DeptAPI.getOptions();
  deptOptions.value = deptData;

  if (user) {
    formData.id = user.id;
    const data = await UserAPI.getFormData(user.id);
    Object.assign(formData, data, { id: user.id });
    // 编辑时回显部门；部门已删除或禁用时不在选项树中，回退到列表行的部门名
    if (data.deptId) {
      deptSelected.value = data.deptId;
      const chain = findOptionChain(deptData, data.deptId);
      deptLabel.value = chain ? chain.map((option) => option.label).join("/") : user.deptName || "";
    }
    // 回显角色（roleIds 与选项 value 统一转字符串比较，兼容数字/字符串ID）
    if (data.roleIds && data.roleIds.length > 0) {
      const roleIds = data.roleIds.map(String);
      const names = roleOptions.value
        .filter((r) => roleIds.includes(String(r.value)))
        .map((r) => r.label);
      roleLabel.value = names.join("、");
    }
  }
}

// 提交表单
function handleUserSubmit() {
  formRef.value.validate().then(({ valid }: { valid: boolean }) => {
    if (!valid) return;
    isSubmitting.value = true;
    const action = formData.id ? UserAPI.update(formData.id, formData) : UserAPI.create(formData);
    action
      .then(() => {
        toast.success("操作成功");
        closeUserDialog();
        loadUserList();
      })
      .finally(() => {
        isSubmitting.value = false;
      });
  });
}

// 关闭弹窗
function closeUserDialog() {
  dialog.visible = false;
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
}

const resetPwdDialog = reactive({
  visible: false,
  isSubmitting: false,
  userId: undefined as number | undefined,
});
const resetPwdForm = reactive({ password: "" });
const resetPwdFormRef = ref();

// 更多操作
function showUserActions(item: UserItem) {
  const menus: ActionMenuOption[] = [];

  // 重置密码
  if (hasPermission("sys:user:reset-password")) {
    menus.push({ name: "重置密码", handler: () => openResetPwdDialog(item) });
  }

  // 编辑
  if (hasPermission("sys:user:update")) {
    menus.push({ name: "编辑", handler: () => openUserDialog(item) });
  }

  // 删除
  if (hasPermission("sys:user:delete")) {
    menus.push({
      name: "删除",
      color: "var(--color-danger)",
      handler: () =>
        confirmAction({
          msg: `确定要删除用户「${item.nickname}」吗？`,
          action: async () => {
            await UserAPI.deleteByIds(String(item.id));
            loadUserList();
          },
        }),
    });
  }

  showActions(menus);
}

// 打开重置密码弹窗
function openResetPwdDialog(item: UserItem) {
  resetPwdForm.password = "";
  resetPwdDialog.userId = item.id;
  resetPwdDialog.visible = true;
  nextTick(() => {
    resetPwdFormRef.value?.reset();
  });
}

// 重置密码
async function handleResetPassword() {
  const valid = await resetPwdFormRef.value?.validate();
  if (!valid || valid.valid === false) return;
  if (!resetPwdDialog.userId) return;

  resetPwdDialog.isSubmitting = true;
  try {
    await UserAPI.resetPassword(resetPwdDialog.userId, resetPwdForm.password);
    toast.success("密码重置成功");
    resetPwdDialog.visible = false;
  } catch (error) {
    // API 已处理错误提示
  } finally {
    resetPwdDialog.isSubmitting = false;
  }
}

onLoad(() => {
  loadUserList();
});
</script>

<script lang="ts">
export default { options: { styleIsolation: "shared" } };
</script>

<style lang="scss" scoped>
.user-card__header {
  display: flex;
  align-items: center;
}

.user-card__avatar {
  flex-shrink: 0;
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
}

.user-card__main {
  flex: 1;
  min-width: 0;
  margin-left: 16rpx;
}

.user-card__name-row {
  display: flex;
  align-items: center;
  min-width: 0;
}

.user-card__name {
  overflow: hidden;
  font-size: 32rpx;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-card__role {
  display: block;
  overflow: hidden;
  font-size: 24rpx;
  color: var(--color-text-secondary);
  text-overflow: ellipsis;
  white-space: nowrap;
}

// 手机号与邮箱：一行放不下自动换行，单个超长时省略号截断
.user-card__contacts {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx 24rpx;
  margin-top: 16rpx;
}

.user-card__contact {
  display: flex;
  align-items: center;
  min-width: 0;
  max-width: 100%;
}

.user-card__contact-text {
  margin-left: 8rpx;
  overflow: hidden;
  font-size: 24rpx;
  color: var(--color-text-secondary);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 8rpx;
  margin-top: 16rpx;
  border-top: 1rpx solid var(--color-border-light);
}
</style>
