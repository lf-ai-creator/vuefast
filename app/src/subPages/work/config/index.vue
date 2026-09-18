<template>
  <view>
    <view>
      <wd-search
        v-model="queryParams.keywords"
        placeholder="搜索配置名称/键名"
        hide-cancel
        @search="handleSearch"
      />
    </view>

    <view class="mt-16rpx">
      <wd-card v-for="item in configs" :key="item.id" @click="openConfigDialog(item.id)">
        <view class="flex-between">
          <text class="font-bold text-32rpx">{{ item.configName }}</text>
          <view
            class="item-action"
            hover-class="item-action--hover"
            @click.stop="showConfigActions(item)"
          >
            <wd-icon name="more" size="18" class="color-text-secondary" />
          </view>
        </view>

        <view class="mt-12rpx">
          <wd-cell-group border>
            <wd-cell title="配置项" :value="item.configKey" ellipsis />
            <wd-cell title="配置值" :value="item.configValue" ellipsis />
            <wd-cell title="描述" :value="item.remark || '暂无描述'" ellipsis />
          </wd-cell-group>
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
      @close="closeConfigDialog"
    >
      <view class="p-4">
        <view class="popup-title">
          {{ formData.id ? "编辑配置" : "新增配置" }}
        </view>
        <wd-form ref="formRef" :model="formData" :schema="rules">
          <wd-form-item prop="configName" title="配置名称" required>
            <wd-input v-model="formData.configName" placeholder="请输入配置名称" />
          </wd-form-item>
          <wd-form-item prop="configKey" title="配置键名" required>
            <wd-input v-model="formData.configKey" placeholder="请输入配置键名" />
          </wd-form-item>
          <wd-form-item prop="configValue" title="配置键值" required>
            <wd-input v-model="formData.configValue" placeholder="请输入配置键值" />
          </wd-form-item>
          <wd-form-item prop="remark" title="描述">
            <wd-textarea
              v-model="formData.remark"
              placeholder="请输入配置描述"
              :maxlength="100"
              show-word-limit
            />
          </wd-form-item>
        </wd-form>
        <view class="popup-actions">
          <wd-button type="info" variant="plain" @click="closeConfigDialog">取消</wd-button>
          <wd-button :loading="isSubmitting" @click="submitConfigForm">保存</wd-button>
        </view>
      </view>
    </wd-popup>

    <!-- 浮动新增按钮 -->
    <wd-fab
      v-if="hasPermission('sys:config:create') && !dialog.visible"
      :expandable="false"
      :gap="{ bottom: 32 }"
    >
      <template #trigger>
        <view class="work-fab-trigger" @click="openConfigDialog()">
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
import ConfigAPI, { type ConfigPageQuery, ConfigItem, ConfigForm } from "@/api/config";
import { hasPermission } from "@/utils/permission";

definePage({
  name: "config",
  style: { navigationBarTitleText: "系统配置", enablePullDownRefresh: true },
});

const toast = useToast();
const { actionSheetVisible, actionSheetActions, showActions, handleActionSelect, confirmAction } =
  useActionSheet();
const formRef = ref();
const isSubmitting = ref(false);

const queryParams = reactive<ConfigPageQuery>({ pageNum: 1, pageSize: 10, keywords: "" });
const dialog = reactive({ visible: false });

// 分页加载（触底加载 + 下拉刷新统一由 usePagedList 维护）
const {
  items: configs,
  total,
  loadMoreState,
  reload,
  retry,
} = usePagedList(ConfigAPI.getPage, queryParams);

const initialFormData: ConfigForm = {
  id: undefined,
  configName: undefined,
  configKey: undefined,
  configValue: undefined,
  remark: undefined,
};

const formData = reactive<ConfigForm>({ ...initialFormData });

const rules = toFormSchema({
  configName: [{ required: true, message: "请输入配置名称" }],
  configKey: [{ required: true, message: "请输入配置键名" }],
  configValue: [{ required: true, message: "请输入配置键值" }],
});

// 搜索触发
const handleSearch = () => loadConfigList();

// 加载列表（回到第一页）
function loadConfigList() {
  reload();
}

// 打开弹窗（新增/编辑）
async function openConfigDialog(id?: number) {
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
  dialog.visible = true;
  if (id) {
    formData.id = id;
    const data = await ConfigAPI.getFormData(id);
    Object.assign(formData, data, { id });
  }
}

// 提交表单
function submitConfigForm() {
  formRef.value.validate().then(({ valid }: { valid: boolean }) => {
    if (!valid) return;
    isSubmitting.value = true;
    const action = formData.id
      ? ConfigAPI.update(formData.id, formData)
      : ConfigAPI.create(formData);
    action
      .then(() => {
        toast.success("操作成功");
        closeConfigDialog();
        loadConfigList();
      })
      .finally(() => {
        isSubmitting.value = false;
      });
  });
}

// 关闭弹窗
function closeConfigDialog() {
  dialog.visible = false;
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
}

// 更多操作
function showConfigActions(item: ConfigItem) {
  const menus: ActionMenuOption[] = [];

  if (hasPermission("sys:config:update")) {
    menus.push({ name: "编辑", handler: () => openConfigDialog(item.id!) });
  }

  if (hasPermission("sys:config:delete")) {
    menus.push({
      name: "删除",
      color: "var(--color-danger)",
      handler: () =>
        confirmAction({
          msg: `确定要删除配置「${item.configName}」吗？`,
          action: async () => {
            await ConfigAPI.deleteByIds(String(item.id!));
            loadConfigList();
          },
        }),
    });
  }

  showActions(menus);
}

onLoad(() => {
  loadConfigList();
});
</script>

<script lang="ts">
export default { options: { styleIsolation: "shared" } };
</script>
