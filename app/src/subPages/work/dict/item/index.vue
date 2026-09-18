<template>
  <view>
    <view>
      <wd-search
        v-model="queryParams.keywords"
        placeholder="搜索字典标签/字典值"
        hide-cancel
        @search="handleSearch"
      />
    </view>

    <view class="mt-16rpx">
      <wd-card v-for="item in dictItems" :key="item.id" @click="openItemDialog(item.id)">
        <view class="flex-start">
          <view class="flex-1">
            <view class="flex-start">
              <text class="font-bold text-32rpx">{{ item.label }}</text>
            </view>
            <text class="text-24rpx color-text-secondary">
              字典值：{{ item.value }} · 排序：{{ item.sort }}
            </text>
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
            @click.stop="showItemActions(item)"
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
      @close="closeItemDialog"
    >
      <view class="p-4">
        <view class="popup-title">
          {{ formData.id ? "编辑字典数据" : "新增字典数据" }}
        </view>
        <wd-form ref="formRef" :model="formData" :schema="rules">
          <wd-form-item prop="label" title="字典项标签" required>
            <wd-input v-model="formData.label" placeholder="请输入字典项标签" />
          </wd-form-item>
          <wd-form-item prop="value" title="字典项值" required>
            <wd-input v-model="formData.value" placeholder="请输入字典项值" />
          </wd-form-item>
          <wd-form-item prop="status" title="状态">
            <wd-switch v-model="formData.status" :active-value="1" :inactive-value="0" />
          </wd-form-item>
          <wd-form-item prop="sort" title="排序">
            <wd-input-number v-model="formData.sort" :min="0" />
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
          <wd-button type="info" variant="plain" @click="closeItemDialog">取消</wd-button>
          <wd-button :loading="isSubmitting" @click="submitItemForm">保存</wd-button>
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
      v-if="hasPermission('sys:dict-item:create') && !dialog.visible"
      :expandable="false"
      :gap="{ bottom: 32 }"
    >
      <template #trigger>
        <view class="work-fab-trigger" @click="openItemDialog()">
          <wd-icon name="plus" size="20" color="var(--color-text-inverse)" />
        </view>
      </template>
    </wd-fab>
  </view>
</template>

<script lang="ts" setup>
import { onLoad } from "@dcloudio/uni-app";
import { toFormSchema } from "@/utils/form-schema";
import { useToast } from "@wot-ui/ui";
import { useActionSheet, type ActionMenuOption } from "@/composables/useActionSheet";
import { usePagedList } from "@/composables/usePagedList";
import DictAPI, { type DictItemForm, type DictItemPageQuery, type DictItem } from "@/api/dict";
import { hasPermission } from "@/utils/permission";

definePage({
  name: "dict-item",
  style: { navigationBarTitleText: "字典数据", enablePullDownRefresh: true },
});

const toast = useToast();
const { actionSheetVisible, actionSheetActions, showActions, handleActionSelect, confirmAction } =
  useActionSheet();

const dictCode = ref<string>("");
const pageTitle = ref<string>("字典数据");

const formRef = ref();
const isSubmitting = ref(false);

const queryParams = reactive<DictItemPageQuery>({ pageNum: 1, pageSize: 10, keywords: "" });
const dialog = reactive({ visible: false });

/**
 * 分页加载（触底加载 + 下拉刷新统一由 usePagedList 维护）
 * dictCode 尚未就绪（onLoad 取参前）时返回空页
 */
const {
  items: dictItems,
  total,
  loadMoreState,
  reload,
  retry,
} = usePagedList(
  (query: DictItemPageQuery) =>
    dictCode.value
      ? DictAPI.getItemPage(dictCode.value, query)
      : Promise.resolve({ list: [], total: 0 }),
  queryParams
);

const initialFormData: DictItemForm = {
  id: undefined,
  dictCode: undefined,
  label: undefined,
  value: undefined,
  sort: 1,
  status: 1,
  remark: undefined,
};

const formData = reactive<DictItemForm>({ ...initialFormData });

const rules = toFormSchema({
  label: [{ required: true, message: "请输入字典项标签" }],
  value: [{ required: true, message: "请输入字典项值" }],
});

const handleSearch = () => loadItemList();

// 加载列表（回到第一页）
function loadItemList() {
  reload();
}

async function openItemDialog(id?: string) {
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
  dialog.visible = true;
  formData.dictCode = dictCode.value;

  if (id) {
    formData.id = id;
    const data = await DictAPI.getItemFormData(dictCode.value, id);
    Object.assign(formData, data, { id });
  }
}

function submitItemForm() {
  formRef.value.validate().then(({ valid }: { valid: boolean }) => {
    if (!valid) return;
    if (!dictCode.value) {
      toast.error("缺少字典编码");
      return;
    }

    isSubmitting.value = true;
    const id = formData.id;
    const action = id
      ? DictAPI.updateItem(dictCode.value, id, formData)
      : DictAPI.createItem(dictCode.value, formData);

    action
      .then(() => {
        toast.success("操作成功");
        closeItemDialog();
        loadItemList();
      })
      .finally(() => {
        isSubmitting.value = false;
      });
  });
}

function closeItemDialog() {
  dialog.visible = false;
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
}

function showItemActions(item: DictItem) {
  const menus: ActionMenuOption[] = [];

  if (hasPermission("sys:dict-item:update")) {
    menus.push({ name: "编辑", handler: () => openItemDialog(item.id) });
  }

  if (hasPermission("sys:dict-item:delete")) {
    menus.push({
      name: "删除",
      color: "var(--color-danger)",
      handler: () =>
        confirmAction({
          msg: `确定要删除字典数据「${item.label}」吗？`,
          action: async () => {
            if (!item.id) return;
            await DictAPI.deleteItems(dictCode.value, String(item.id));
            loadItemList();
          },
        }),
    });
  }

  showActions(menus);
}

onLoad((query) => {
  dictCode.value = String(query?.dictCode || "");
  pageTitle.value = String(query?.title || "字典数据");
  if (pageTitle.value) {
    uni.setNavigationBarTitle({ title: pageTitle.value });
  }
  loadItemList();
});
</script>

<script lang="ts">
export default { options: { styleIsolation: "shared" } };
</script>
