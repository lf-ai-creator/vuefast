<template>
  <view>
    <view>
      <wd-search
        v-model="queryParams.keywords"
        placeholder="搜索菜单名称"
        hide-cancel
        @search="handleSearch"
      />
    </view>

    <!-- 菜单树形列表 -->
    <view class="mt-16rpx">
      <custom-tree
        :data="treeData"
        :default-expand-all="true"
        :show-action="true"
        @action="handleNodeAction"
      >
        <!-- 自定义节点内容：ID + 名称 + 状态 -->
        <template #content="{ node }">
          <view class="flex-1 flex-start gap-16rpx">
            <text class="w-120rpx text-24rpx color-text-secondary">{{ node.id }}</text>
            <wd-icon v-if="node.icon" :name="node.icon" size="16" class="color-primary" />
            <text class="flex-1 truncate">{{ node.name }}</text>
            <wd-tag class="flex-shrink-0" :type="getMenuTypeTag(node.type)" size="small">
              {{ getMenuTypeText(node.type) }}
            </wd-tag>
            <wd-tag
              class="flex-shrink-0"
              :type="node.visible === 1 ? 'success' : 'primary'"
              size="small"
            >
              {{ node.visible === 1 ? "显示" : "隐藏" }}
            </wd-tag>
          </view>
        </template>
      </custom-tree>

      <wd-empty v-if="menuList.length === 0" icon="search-line" tip="暂无数据" />
    </view>

    <!-- 弹窗表单 -->
    <wd-popup
      v-model="dialog.visible"
      position="bottom"
      custom-class="popup-bottom-scroll"
      @close="closeMenuDialog"
    >
      <view class="p-4">
        <view class="popup-title">
          {{ formData.id ? "编辑菜单" : "新增菜单" }}
        </view>
        <scroll-view scroll-y class="max-h-60vh">
          <wd-form ref="formRef" :model="formData" :schema="rules">
            <!-- 上级菜单选择：触发交 wd-form-item，选择器只负责弹出 -->
            <wd-form-item
              title="上级菜单"
              prop="parentId"
              required
              is-link
              :value="parentLabel"
              placeholder="请选择上级菜单"
              @click="showParentPicker = true"
            />
            <wd-cascader
              v-model="parentSelected"
              v-model:visible="showParentPicker"
              :options="parentOptions"
              text-key="label"
              @confirm="handleParentConfirm"
            />
            <wd-form-item prop="name" title="菜单名称" required>
              <wd-input v-model="formData.name" placeholder="请输入菜单名称" />
            </wd-form-item>
            <wd-form-item prop="type" title="菜单类型" required>
              <wd-radio-group v-model="formData.type" size="small" type="button">
                <wd-radio value="C">目录</wd-radio>
                <wd-radio value="M">菜单</wd-radio>
                <wd-radio value="E">外链</wd-radio>
                <wd-radio value="B">按钮</wd-radio>
              </wd-radio-group>
            </wd-form-item>
            <wd-form-item
              v-if="formData.type === 'C' || formData.type === 'M'"
              prop="routePath"
              title="路由路径"
            >
              <wd-input v-model="formData.routePath" placeholder="system 或 /system" />
            </wd-form-item>
            <wd-form-item v-if="formData.type === 'E'" prop="externalUrl" title="外链地址">
              <wd-input v-model="formData.externalUrl" placeholder="https://example.com" />
            </wd-form-item>
            <wd-form-item v-if="formData.type === 'M'" prop="component" title="组件路径">
              <wd-input v-model="formData.component" placeholder="system/menu/index" />
            </wd-form-item>
            <wd-form-item v-if="formData.type === 'B'" prop="perm" title="权限标识">
              <wd-input v-model="formData.perm" placeholder="sys:menu:create" />
            </wd-form-item>
            <wd-form-item prop="icon" title="图标">
              <wd-input v-model="formData.icon" placeholder="请输入图标名" />
            </wd-form-item>
            <wd-form-item prop="sort" title="排序">
              <wd-input-number v-model="formData.sort!" :min="0" />
            </wd-form-item>
            <wd-form-item prop="visible" title="状态">
              <wd-switch v-model="formData.visible" :active-value="1" :inactive-value="0" />
            </wd-form-item>
          </wd-form>
        </scroll-view>
        <view class="popup-actions">
          <wd-button type="info" variant="plain" @click="closeMenuDialog">取消</wd-button>
          <wd-button :loading="isSubmitting" @click="submitMenuForm">保存</wd-button>
        </view>
      </view>
    </wd-popup>

    <!-- 浮动新增按钮 -->
    <wd-fab
      v-if="hasPermission('sys:menu:create') && !dialog.visible"
      :expandable="false"
      :gap="{ bottom: 32 }"
    >
      <template #trigger>
        <view class="work-fab-trigger" @click="openMenuDialog()">
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
import { useActionSheet, type ActionMenuOption } from "@/composables/useActionSheet";
import MenuAPI, { type MenuQuery, MenuItem, MenuForm } from "@/api/menu";
import { hasPermission } from "@/utils/permission";
import CustomTree, { type TreeOption } from "@/subPages/work/components/custom-tree.vue";
import type { CascaderOption } from "@wot-ui/ui/components/wd-cascader/types";

definePage({
  name: "menu",
  style: { navigationBarTitleText: "菜单管理" },
});

const toast = useToast();
const { actionSheetVisible, actionSheetActions, showActions, handleActionSelect, confirmAction } =
  useActionSheet();
const formRef = ref();
const isSubmitting = ref(false);

const queryParams = reactive<MenuQuery>({ keywords: "" });
const menuList = ref<MenuItem[]>([]);
const dialog = reactive({ visible: false });

const initialFormData: MenuForm = {
  id: undefined,
  parentId: "0",
  name: undefined,
  type: "M",
  routePath: undefined,
  component: undefined,
  externalUrl: undefined,
  perm: undefined,
  icon: undefined,
  sort: 1,
  visible: 1,
};

const formData = reactive<MenuForm>({ ...initialFormData });

// 转换为树组件数据格式
const treeData = computed(() => menuList.value.map((menu: MenuItem) => transformMenuToTree(menu)));

function transformMenuToTree(menu: MenuItem): TreeOption {
  return {
    value: menu.id ?? "",
    label: menu.name ?? "",
    id: menu.id,
    name: menu.name,
    type: menu.type,
    icon: menu.icon,
    visible: menu.visible,
    perm: menu.perm,
    children: menu.children?.map((child: MenuItem) => transformMenuToTree(child)) || [],
  };
}

// 菜单类型标签
function normalizeMenuType(type?: string | number) {
  if (type === 1 || type === "1") return "C";
  if (type === 2 || type === "2") return "M";
  if (type === 3 || type === "3") return "B";
  return type;
}

function getMenuTypeTag(type?: string | number): "primary" | "success" | "warning" | "danger" {
  const map: Record<string, "primary" | "success" | "warning" | "danger"> = {
    C: "warning",
    M: "success",
    E: "primary",
    B: "danger",
  };
  const key = String(normalizeMenuType(type) || "M");
  return map[key] || "primary";
}

function getMenuTypeText(type?: string | number) {
  const map: Record<string, string> = { C: "目录", M: "菜单", E: "外链", B: "按钮" };
  const key = String(normalizeMenuType(type) || "M");
  return map[key] || "菜单";
}

// 上级菜单选择器
const showParentPicker = ref(false);
const parentSelected = ref<string | number>("");
const parentOptions = ref<OptionType[]>([]);
const parentLabel = ref("");

// 上级菜单确认选择
const handleParentConfirm = ({
  value,
  selectedOptions,
}: {
  value: string | number;
  selectedOptions: CascaderOption[];
}) => {
  parentSelected.value = value;
  formData.parentId = String(value) || "0";
  parentLabel.value = selectedOptions.map((item) => String(item.label ?? "")).join("/");
};

const rules = toFormSchema({
  name: [{ required: true, message: "请输入菜单名称" }],
  type: [{ required: true, message: "请选择菜单类型" }],
  parentId: [{ required: true, message: "请选择上级菜单" }],
});

const handleSearch = () => loadMenuList();

function loadMenuList() {
  MenuAPI.getList(queryParams).then((data) => {
    menuList.value = data;
  });
}

// 处理节点操作按钮点击
function handleNodeAction(node: TreeOption) {
  const menu: MenuItem = {
    id: node.id,
    name: node.label,
    type: node.type,
    visible: node.visible,
    children: node.children,
  } as MenuItem;

  const menus: ActionMenuOption[] = [];

  // 按钮(B)类型节点不允许再有下级
  if (hasPermission("sys:menu:create") && normalizeMenuType(String(node.type)) !== "B") {
    menus.push({ name: "新增子菜单", handler: () => handleAddChild(menu) });
  }

  if (hasPermission("sys:menu:update")) {
    menus.push({ name: "编辑", handler: () => openMenuDialog(menu) });
  }

  if (hasPermission("sys:menu:delete")) {
    menus.push({
      name: "删除",
      color: "var(--color-danger)",
      handler: () =>
        confirmAction({
          msg: `确定要删除菜单「${menu.name}」吗？`,
          action: async () => {
            await MenuAPI.deleteByIds(menu.id!);
            loadMenuList();
          },
        }),
    });
  }

  showActions(menus);
}

// 打开弹窗（新增/编辑）
async function openMenuDialog(menu?: MenuItem) {
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
  parentSelected.value = "";
  parentLabel.value = "";
  dialog.visible = true;

  const data = await MenuAPI.getOptions(true);
  parentOptions.value = [{ value: "0", label: "顶级菜单" }, ...data];

  if (menu?.id) {
    formData.id = menu.id;
    const form = await MenuAPI.getFormData(menu.id);
    Object.assign(formData, form, { id: menu.id });

    // 编辑时回显上级菜单
    if (String(form.parentId) === "0") {
      parentSelected.value = "0";
      parentLabel.value = "顶级菜单";
    } else if (form.parentId) {
      parentSelected.value = form.parentId;
      const chain = findOptionChain(data, form.parentId);
      parentLabel.value = chain ? chain.map((option) => option.label).join("/") : "";
    }
  }
}

// 新增子菜单：按新增流程打开弹窗，并预设上级菜单
function handleAddChild(menu: MenuItem) {
  openMenuDialog();
  formData.parentId = menu.id!;
  parentSelected.value = menu.id!;
  parentLabel.value =
    findOptionChain(treeData.value, menu.id!)
      ?.map((option) => option.label)
      .join("/") ||
    menu.name ||
    "";
}

// 按类型清理无关字段，避免误提交
function normalizeMenuPayload() {
  const payload: MenuForm = { ...formData };

  if (payload.type === "E") {
    payload.routePath = undefined;
    payload.component = undefined;
    payload.perm = undefined;
  } else {
    payload.externalUrl = undefined;
  }

  if (payload.type === "B") {
    payload.routePath = undefined;
    payload.component = undefined;
    payload.icon = undefined;
  }

  return payload;
}

// 提交表单
function submitMenuForm() {
  formRef.value.validate().then(({ valid }: { valid: boolean }) => {
    if (!valid) return;
    isSubmitting.value = true;
    const payload = normalizeMenuPayload();
    const action = formData.id ? MenuAPI.update(formData.id, payload) : MenuAPI.create(payload);
    action
      .then(() => {
        toast.success("操作成功");
        closeMenuDialog();
        loadMenuList();
      })
      .finally(() => {
        isSubmitting.value = false;
      });
  });
}

// 关闭弹窗
function closeMenuDialog() {
  dialog.visible = false;
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
}

onLoad(() => {
  loadMenuList();
});
</script>

<script lang="ts">
export default { options: { styleIsolation: "shared" } };
</script>
