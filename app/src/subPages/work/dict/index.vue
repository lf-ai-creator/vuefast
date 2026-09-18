<template>
  <view>
    <view>
      <wd-search
        v-model="queryParams.keywords"
        placeholder="搜索字典名称/编码"
        hide-cancel
        @search="handleSearch"
      />
    </view>

    <view class="mt-16rpx">
      <wd-card v-for="item in dicts" :key="item.id" @click="openDictItemPage(item)">
        <view class="flex-start">
          <view class="flex-1">
            <view class="flex-start">
              <text class="font-bold text-32rpx">{{ item.name }}</text>
            </view>
            <text class="text-24rpx color-text-secondary">字典编码：{{ item.dictCode }}</text>
          </view>
          <wd-tag :type="item.status === 1 ? 'success' : 'danger'">
            {{ item.status === 1 ? "启用" : "禁用" }}
          </wd-tag>
        </view>

        <view class="flex-between mt-16rpx">
          <text class="text-24rpx color-text-placeholder">{{ item.remark || "暂无备注" }}</text>
          <view
            class="item-action"
            hover-class="item-action--hover"
            @click.stop="showDictActions(item)"
          >
            <wd-icon name="more" size="18" class="color-text-secondary" />
          </view>
        </view>
      </wd-card>

      <wd-loadmore v-if="loadMoreState !== 'idle'" :state="loadMoreState" @reload="retry" />
      <wd-empty v-else-if="total === 0" icon="search-line" tip="暂无数据" />
    </view>

    <wd-popup
      v-model="dialog.visible"
      position="bottom"
      custom-class="popup-bottom"
      @close="closeDictDialog"
    >
      <view class="p-4">
        <view class="popup-title">
          {{ formData.id ? "编辑字典" : "新增字典" }}
        </view>
        <wd-form ref="formRef" :model="formData" :schema="rules">
          <wd-form-item prop="name" title="字典名称" required>
            <wd-input v-model="formData.name" placeholder="请输入字典名称" />
          </wd-form-item>
          <wd-form-item prop="dictCode" title="字典编码" required>
            <wd-input v-model="formData.dictCode" placeholder="请输入字典编码" />
          </wd-form-item>
          <wd-form-item prop="status" title="状态">
            <wd-switch v-model="formData.status" :active-value="1" :inactive-value="0" />
          </wd-form-item>
          <wd-form-item prop="remark" title="备注">
            <wd-textarea
              v-model="formData.remark"
              placeholder="请输入备注"
              :maxlength="100"
              show-word-limit
            />
          </wd-form-item>
        </wd-form>
        <view class="popup-actions">
          <wd-button type="info" variant="plain" @click="closeDictDialog">取消</wd-button>
          <wd-button :loading="isSubmitting" @click="submitDictForm">保存</wd-button>
        </view>
      </view>
    </wd-popup>

    <wd-action-sheet
      v-model="actionSheetVisible"
      :actions="actionSheetActions"
      cancel-text="取消"
      @select="handleActionSelect"
    />
    <wd-fab
      v-if="hasPermission('sys:dict:create') && !dialog.visible"
      :expandable="false"
      :gap="{ bottom: 32 }"
    >
      <template #trigger>
        <view class="work-fab-trigger" @click="openDictDialog()">
          <wd-icon name="plus" size="20" color="var(--color-text-inverse)" />
        </view>
      </template>
    </wd-fab>
  </view>
</template>

<script lang="ts" setup>
import { onLoad } from "@dcloudio/uni-app";
import { useRouter } from "uni-mini-router";
import { toFormSchema } from "@/utils/form-schema";
import { useToast } from "@wot-ui/ui";
import { useActionSheet, type ActionMenuOption } from "@/composables/useActionSheet";
import { usePagedList } from "@/composables/usePagedList";
import DictAPI, { type DictTypeForm, type DictTypePageQuery, type DictTypeItem } from "@/api/dict";
import { hasPermission } from "@/utils/permission";

definePage({
  name: "dict",
  style: { navigationBarTitleText: "字典管理", enablePullDownRefresh: true },
});

const router = useRouter();
const toast = useToast();
const { actionSheetVisible, actionSheetActions, showActions, handleActionSelect, confirmAction } =
  useActionSheet();
const formRef = ref();
const isSubmitting = ref(false);

const queryParams = reactive<DictTypePageQuery>({ pageNum: 1, pageSize: 10, keywords: "" });
const dialog = reactive({ visible: false });

// 分页加载（触底加载 + 下拉刷新统一由 usePagedList 维护）
const {
  items: dicts,
  total,
  loadMoreState,
  reload,
  retry,
} = usePagedList(DictAPI.getPage, queryParams);

const initialFormData: DictTypeForm = {
  id: undefined,
  name: undefined,
  dictCode: undefined,
  status: 1,
  remark: undefined,
};

const formData = reactive<DictTypeForm>({ ...initialFormData });

const rules = toFormSchema({
  name: [{ required: true, message: "请输入字典名称" }],
  dictCode: [{ required: true, message: "请输入字典编码" }],
});

const handleSearch = () => loadDictTypeList();

// 加载列表（回到第一页）
function loadDictTypeList() {
  reload();
}

function openDictItemPage(item: DictTypeItem) {
  if (!item.dictCode) return;
  router.push({
    path: "/subPages/work/dict/item/index",
    query: { dictCode: item.dictCode, title: `【${item.name}】字典数据` },
  });
}

async function openDictDialog(id?: string) {
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
  dialog.visible = true;
  if (id) {
    formData.id = id;
    const data = await DictAPI.getFormData(id);
    Object.assign(formData, data, { id });
  }
}

function submitDictForm() {
  formRef.value.validate().then(({ valid }: { valid: boolean }) => {
    if (!valid) return;
    isSubmitting.value = true;
    const id = formData.id;
    const action = id ? DictAPI.update(id, formData) : DictAPI.create(formData);
    action
      .then(() => {
        toast.success("操作成功");
        closeDictDialog();
        loadDictTypeList();
      })
      .finally(() => {
        isSubmitting.value = false;
      });
  });
}

function closeDictDialog() {
  dialog.visible = false;
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
}

function showDictActions(item: DictTypeItem) {
  const menus: ActionMenuOption[] = [{ name: "字典数据", handler: () => openDictItemPage(item) }];

  if (hasPermission("sys:dict:update")) {
    menus.push({ name: "编辑", handler: () => openDictDialog(item.id) });
  }

  if (hasPermission("sys:dict:delete")) {
    menus.push({
      name: "删除",
      color: "var(--color-danger)",
      handler: () =>
        confirmAction({
          msg: `确定要删除字典「${item.name}」吗？`,
          action: async () => {
            if (!item.id) return;
            await DictAPI.deleteByIds(String(item.id));
            loadDictTypeList();
          },
        }),
    });
  }

  showActions(menus);
}

onLoad(() => {
  loadDictTypeList();
});
</script>

<script lang="ts">
export default { options: { styleIsolation: "shared" } };
</script>
