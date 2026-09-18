<template>
  <view>
    <view>
      <wd-search
        v-model="queryParams.keywords"
        placeholder="搜索部门名称"
        hide-cancel
        @search="handleSearch"
      />
    </view>

    <!-- 部门树形列表 -->
    <view class="mt-16rpx">
      <CustomTree
        :data="treeData"
        :default-expand-all="true"
        :show-action="true"
        @action="handleNodeAction"
      >
        <!-- 自定义节点内容：ID + 名称 + 状态 -->
        <template #content="{ node }">
          <view class="flex-1 flex-start gap-16rpx">
            <text class="w-120rpx text-24rpx color-text-secondary">{{ node.id }}</text>
            <text class="flex-1 truncate">{{ node.name }}</text>
            <wd-tag :type="node.status === 1 ? 'success' : 'danger'" size="small">
              {{ node.status === 1 ? "正常" : "禁用" }}
            </wd-tag>
          </view>
        </template>
      </CustomTree>

      <wd-empty v-if="deptList.length === 0" icon="search-line" tip="暂无数据" />
    </view>

    <!-- 弹窗表单 -->
    <wd-popup
      v-model="dialog.visible"
      position="bottom"
      custom-class="popup-bottom"
      @close="closeDeptDialog"
    >
      <view class="p-4">
        <view class="popup-title">
          {{ formData.id ? "编辑部门" : "新增部门" }}
        </view>
        <wd-form ref="formRef" :model="formData" :schema="rules">
          <!-- 上级部门选择：触发交 wd-form-item，选择器只负责弹出 -->
          <wd-form-item
            title="上级部门"
            prop="parentId"
            required
            is-link
            :value="parentLabel"
            placeholder="请选择上级部门"
            @click="showParentPicker = true"
          />
          <wd-cascader
            v-model="parentSelected"
            v-model:visible="showParentPicker"
            :options="parentOptions"
            text-key="label"
            @confirm="handleParentConfirm"
          />
          <wd-form-item prop="name" title="部门名称" required>
            <wd-input v-model="formData.name" placeholder="请输入部门名称" />
          </wd-form-item>
          <wd-form-item prop="code" title="部门编号" required>
            <wd-input v-model="formData.code" placeholder="请输入部门编号" />
          </wd-form-item>
          <wd-form-item prop="sort" title="排序">
            <wd-input-number v-model="formData.sort!" :min="0" />
          </wd-form-item>
          <wd-form-item prop="status" title="状态">
            <wd-switch v-model="formData.status" :active-value="1" :inactive-value="0" />
          </wd-form-item>
        </wd-form>
        <view class="popup-actions">
          <wd-button type="info" variant="plain" @click="closeDeptDialog">取消</wd-button>
          <wd-button :loading="isSubmitting" @click="submitDeptForm">保存</wd-button>
        </view>
      </view>
    </wd-popup>

    <!-- 浮动新增按钮 -->
    <wd-fab
      v-if="hasPermission('sys:dept:create') && !dialog.visible"
      :expandable="false"
      :gap="{ bottom: 32 }"
    >
      <template #trigger>
        <view class="work-fab-trigger" @click="openDeptDialog()">
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
import { findOptionChain } from "@/utils/tree";
import { useToast } from "@wot-ui/ui";
import type { CascaderOption } from "@wot-ui/ui/components/wd-cascader/types";
import { useActionSheet, type ActionMenuOption } from "@/composables/useActionSheet";
import DeptAPI, { type DeptQuery, DeptItem, DeptForm } from "@/api/dept";
import { hasPermission } from "@/utils/permission";
import CustomTree, { type TreeOption } from "@/subPages/work/components/custom-tree.vue";

definePage({
  name: "dept",
  style: { navigationBarTitleText: "部门管理" },
});

const toast = useToast();
const { actionSheetVisible, actionSheetActions, showActions, handleActionSelect, confirmAction } =
  useActionSheet();
const formRef = ref();
const isSubmitting = ref(false);

const queryParams = reactive<DeptQuery>({ keywords: "" });
const deptList = ref<DeptItem[]>([]);
const dialog = reactive({ visible: false });

const initialFormData: DeptForm = {
  id: undefined,
  parentId: 0,
  name: undefined,
  code: undefined,
  sort: 1,
  status: 1,
};

const formData = reactive<DeptForm>({ ...initialFormData });

// 转换为树组件数据格式
const treeData = computed(() => deptList.value.map((dept) => transformDeptToTree(dept)));

function transformDeptToTree(dept: DeptItem): TreeOption {
  return {
    value: String(dept.id),
    label: dept.name ?? "",
    id: dept.id,
    name: dept.name,
    status: dept.status,
    children: dept.children?.map((child) => transformDeptToTree(child)) || [],
  };
}

// 上级部门选择器
const showParentPicker = ref(false);
const parentSelected = ref<string | number>("");
const parentOptions = ref<OptionType[]>([]);
const parentLabel = ref("");

// 上级部门确认选择
const handleParentConfirm = ({
  value,
  selectedOptions,
}: {
  value: string | number;
  selectedOptions: CascaderOption[];
}) => {
  parentSelected.value = value;
  formData.parentId = Number(value) || 0;
  parentLabel.value = selectedOptions.map((item) => String(item.label ?? "")).join("/");
};

const rules = toFormSchema({
  name: [{ required: true, message: "请输入部门名称" }],
  code: [{ required: true, message: "请输入部门编号" }],
  parentId: [{ required: true, message: "请选择上级部门" }],
});

// 搜索触发
const handleSearch = () => loadDeptList();

// 加载列表
function loadDeptList() {
  DeptAPI.getList(queryParams)
    .then((data) => {
      deptList.value = data;
    })
    .catch(() => {
      // API 层已处理错误提示
    });
}

// 处理节点操作按钮点击
function handleNodeAction(node: TreeOption) {
  const dept: DeptItem = {
    id: node.id,
    name: node.label,
    status: node.status,
    children: node.children,
  } as DeptItem;

  const menus: ActionMenuOption[] = [];

  if (hasPermission("sys:dept:create")) {
    menus.push({ name: "新增子部门", handler: () => handleAddChild(dept) });
  }

  if (hasPermission("sys:dept:update")) {
    menus.push({ name: "编辑", handler: () => openDeptDialog(dept) });
  }

  if (hasPermission("sys:dept:delete")) {
    menus.push({
      name: "删除",
      color: "var(--color-danger)",
      handler: () =>
        confirmAction({
          msg: `确定要删除部门「${dept.name}」吗？`,
          action: async () => {
            await DeptAPI.deleteByIds(String(dept.id));
            loadDeptList();
          },
        }),
    });
  }

  showActions(menus);
}

// 打开弹窗（新增/编辑）
async function openDeptDialog(dept?: DeptItem) {
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
  parentSelected.value = "";
  parentLabel.value = "";
  dialog.visible = true;

  const data = await DeptAPI.getOptions();
  parentOptions.value = [{ value: "0", label: "顶级部门" }, ...data];

  if (dept?.id) {
    formData.id = dept.id;
    const form = await DeptAPI.getFormData(dept.id);
    Object.assign(formData, form, { id: dept.id });

    // 编辑时回显上级部门
    if (form.parentId === 0) {
      parentSelected.value = "0";
      parentLabel.value = "顶级部门";
    } else if (form.parentId) {
      parentSelected.value = form.parentId;
      const chain = findOptionChain(data, form.parentId);
      parentLabel.value = chain ? chain.map((option) => option.label).join("/") : "";
    }
  }
}

// 新增子部门：按新增流程打开弹窗，并预设上级部门
function handleAddChild(dept: DeptItem) {
  openDeptDialog();
  formData.parentId = dept.id!;
  parentSelected.value = dept.id!;
  parentLabel.value =
    findOptionChain(treeData.value, dept.id!)
      ?.map((option) => option.label)
      .join("/") ||
    dept.name ||
    "";
}

// 提交表单
function submitDeptForm() {
  formRef.value.validate().then(({ valid }: { valid: boolean }) => {
    if (!valid) return;
    isSubmitting.value = true;
    const action = formData.id ? DeptAPI.update(formData.id, formData) : DeptAPI.create(formData);
    action
      .then(() => {
        toast.success("操作成功");
        closeDeptDialog();
        loadDeptList();
      })
      .finally(() => {
        isSubmitting.value = false;
      });
  });
}

// 关闭弹窗
function closeDeptDialog() {
  dialog.visible = false;
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
}

onLoad(() => {
  loadDeptList();
});
</script>

<script lang="ts">
export default { options: { styleIsolation: "shared" } };
</script>
