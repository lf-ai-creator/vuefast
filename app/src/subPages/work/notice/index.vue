<template>
  <view>
    <view>
      <wd-search
        v-model="queryParams.title"
        placeholder="搜索通知标题"
        hide-cancel
        @search="handleSearch"
      />
    </view>

    <!-- 通知列表 -->
    <view class="mt-16rpx">
      <wd-card v-for="item in notices" :key="item.id" @click="openNoticeDetail(item)">
        <!-- 主信息行 -->
        <view class="flex-start">
          <view class="notice-card__main">
            <view class="flex-start mt-12rpx">
              <text class="notice-card__title">{{ item.title }}</text>
            </view>
            <text class="notice-card__publisher">
              {{ item.publisherName || "系统管理员" }}
            </text>
          </view>
          <wd-tag :type="getStatusType(item.publishStatus)">
            {{ getStatusText(item.publishStatus) }}
          </wd-tag>
        </view>

        <!-- 辅助信息行 -->
        <view class="notice-card__meta">
          <view class="notice-card__detail">
            <wd-icon name="user" size="16" class="color-text-secondary" />
            <text class="notice-card__detail-text">
              {{ item.targetType === 1 ? "全体" : "指定用户" }}
            </text>
          </view>
          <view class="notice-card__detail">
            <wd-icon name="info-circle" size="16" class="color-text-secondary" />
            <text class="notice-card__detail-text">
              {{ getLevelText(item.level) }}
            </text>
          </view>
        </view>

        <!-- 元信息行 -->
        <view class="notice-card__footer">
          <text class="item-time">{{ formatTime(item) }}</text>
          <view
            class="item-action"
            hover-class="item-action--hover"
            @click.stop="showNoticeActions(item)"
          >
            <wd-icon name="more" size="16" class="color-text-secondary" />
          </view>
        </view>
      </wd-card>

      <wd-loadmore v-if="loadMoreState !== 'idle'" :state="loadMoreState" @reload="retry" />
      <wd-empty v-else-if="total === 0" icon="search-line" tip="暂无数据" />
    </view>

    <!-- 详情弹窗 -->
    <wd-popup
      v-model="detailDialog.visible"
      position="bottom"
      custom-class="popup-bottom"
      @close="closeNoticeDetail"
    >
      <view class="p-4">
        <view class="popup-title">通知详情</view>
        <wd-cell-group border>
          <wd-cell title="标题" :value="noticeDetail.title" />
          <wd-cell title="发布状态">
            <template #default>
              <wd-tag :type="getStatusType(noticeDetail.publishStatus)" size="small">
                {{ getStatusText(noticeDetail.publishStatus) }}
              </wd-tag>
            </template>
          </wd-cell>
          <wd-cell title="发布人" :value="noticeDetail.publisherName" />
          <wd-cell title="发布时间" :value="formatDateTime(noticeDetail.publishTime) || '-'" />
        </wd-cell-group>
        <view class="mt-4 p-4 bg-[var(--color-fill-1)] rounded-lg">
          <rich-text :nodes="noticeDetail.content" class="text-28rpx" />
        </view>
        <view class="popup-actions">
          <wd-button type="info" variant="plain" block @click="closeNoticeDetail">关闭</wd-button>
        </view>
      </view>
    </wd-popup>

    <!-- 新增/编辑弹窗 -->
    <wd-popup
      v-model="dialog.visible"
      position="bottom"
      custom-class="popup-bottom"
      @close="closeNoticeDialog"
    >
      <view class="p-4">
        <view class="popup-title">
          {{ formData.id ? "编辑通知" : "新增通知" }}
        </view>
        <wd-form ref="formRef" :model="formData" :schema="formRules">
          <wd-form-item prop="title" title="标题" required>
            <wd-input v-model="formData.title" placeholder="请输入通知标题" />
          </wd-form-item>
          <wd-form-item prop="level" title="优先级">
            <wd-radio-group v-model="formData.level" type="button">
              <wd-radio value="L">低</wd-radio>
              <wd-radio value="M">中</wd-radio>
              <wd-radio value="H">高</wd-radio>
            </wd-radio-group>
          </wd-form-item>
          <wd-form-item prop="targetType" title="目标类型">
            <wd-radio-group v-model="formData.targetType" type="button">
              <wd-radio :value="1">全体</wd-radio>
              <wd-radio :value="2">指定用户</wd-radio>
            </wd-radio-group>
          </wd-form-item>
          <wd-form-item prop="content" title="内容">
            <wd-textarea
              v-model="formData.content"
              placeholder="请输入通知内容"
              :maxlength="500"
              show-word-limit
            />
          </wd-form-item>
        </wd-form>
        <view class="popup-actions">
          <wd-button type="info" variant="plain" @click="closeNoticeDialog">取消</wd-button>
          <wd-button :loading="isSubmitting" @click="submitNoticeForm">保存</wd-button>
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
      v-if="hasPermission('sys:notice:create') && !dialog.visible && !detailDialog.visible"
      :expandable="false"
      :gap="{ bottom: 32 }"
    >
      <template #trigger>
        <view class="work-fab-trigger" @click="openNoticeDialog()">
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
import NoticeAPI, {
  type NoticePageQuery,
  NoticeItem,
  NoticeDetail,
  NoticeForm,
} from "@/api/notice";
import { hasPermission } from "@/utils/permission";
import { formatDateTime } from "@/utils/format";

definePage({
  name: "notice",
  style: { navigationBarTitleText: "通知公告", enablePullDownRefresh: true },
});

const toast = useToast();
const { actionSheetVisible, actionSheetActions, showActions, handleActionSelect, confirmAction } =
  useActionSheet();
const formRef = ref();
const isSubmitting = ref(false);

const queryParams = reactive<NoticePageQuery>({ pageNum: 1, pageSize: 10 });

// 分页加载（触底加载 + 下拉刷新统一由 usePagedList 维护）
const {
  items: notices,
  total,
  loadMoreState,
  reload,
  retry,
} = usePagedList(NoticeAPI.getPage, queryParams);

const noticeDetail = ref<NoticeDetail>({});
const detailDialog = reactive({ visible: false });

const dialog = reactive({ visible: false });
const initialFormData: NoticeForm = {
  id: undefined,
  title: undefined,
  content: undefined,
  type: undefined,
  level: "M",
  targetType: 1,
  targetUserIds: undefined,
};
const formData = reactive<NoticeForm>({ ...initialFormData });

const formRules = toFormSchema({
  title: [{ required: true, message: "请输入通知标题" }],
});

// 获取状态样式
const getStatusType = (
  status?: number
): "default" | "primary" | "danger" | "warning" | "success" => {
  const map: Record<number, "default" | "primary" | "danger" | "warning" | "success"> = {
    0: "primary",
    1: "success",
    [-1]: "warning",
  };
  return status !== undefined ? map[status] || "default" : "default";
};

// 获取状态文本
const getStatusText = (status?: number): string => {
  const map: Record<number, string> = { 0: "未发布", 1: "已发布", [-1]: "已撤回" };
  return status !== undefined ? map[status] || "未知" : "-";
};

// 获取级别文本
const getLevelText = (level?: string | number): string => {
  const map: Record<string, string> = { L: "低", M: "中", H: "高" };
  return level ? map[String(level)] || String(level) : "-";
};

// 格式化时间
const formatTime = (item: NoticeItem): string => {
  if (item.publishStatus === 1 && item.publishTime) {
    return formatDateTime(item.publishTime);
  }
  if (item.publishStatus === -1 && item.revokeTime) {
    return formatDateTime(item.revokeTime);
  }
  return "-";
};

// 搜索触发
const handleSearch = () => loadNoticeList();

// 加载列表（回到第一页）
function loadNoticeList() {
  reload();
}

// 打开详情弹窗
async function openNoticeDetail(item: NoticeItem) {
  const detail = await NoticeAPI.getDetail(item.id);
  noticeDetail.value = detail;
  detailDialog.visible = true;
}

// 关闭详情弹窗
function closeNoticeDetail() {
  detailDialog.visible = false;
}

// 打开表单弹窗
async function openNoticeDialog(id?: number) {
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
  dialog.visible = true;
  if (id) {
    formData.id = id;
    const data = await NoticeAPI.getFormData(id);
    Object.assign(formData, data, { id });
  }
}

// 关闭表单弹窗
function closeNoticeDialog() {
  dialog.visible = false;
  formRef.value?.reset();
  Object.assign(formData, initialFormData);
}

// 提交表单
function submitNoticeForm() {
  formRef.value.validate().then(({ valid }: { valid: boolean }) => {
    if (!valid) return;
    isSubmitting.value = true;
    const id = formData.id;
    const action = id ? NoticeAPI.update(id, formData) : NoticeAPI.create(formData);
    action
      .then(() => {
        toast.success("操作成功");
        closeNoticeDialog();
        loadNoticeList();
      })
      .finally(() => {
        isSubmitting.value = false;
      });
  });
}

// 更多操作
function showNoticeActions(item: NoticeItem) {
  const menus: ActionMenuOption[] = [{ name: "查看", handler: () => openNoticeDetail(item) }];

  if (item.publishStatus !== 1) {
    if (hasPermission("sys:notice:update")) {
      menus.push({ name: "编辑", handler: () => openNoticeDialog(Number(item.id)) });
    }
    if (hasPermission("sys:notice:delete")) {
      menus.push({
        name: "删除",
        color: "var(--color-danger)",
        handler: () =>
          confirmAction({
            msg: `确定要删除通知「${item.title}」吗？`,
            action: async () => {
              await NoticeAPI.deleteByIds(item.id);
              loadNoticeList();
            },
          }),
      });
    }
    if (hasPermission("sys:notice:publish")) {
      menus.push({
        name: "发布",
        handler: () =>
          confirmAction({
            title: "确认发布",
            msg: `确定要发布通知「${item.title}」吗？`,
            successText: "发布成功",
            action: async () => {
              await NoticeAPI.publish(Number(item.id));
              loadNoticeList();
            },
          }),
      });
    }
  } else if (hasPermission("sys:notice:revoke")) {
    menus.push({
      name: "撤回",
      color: "var(--color-warning)",
      handler: () =>
        confirmAction({
          title: "确认撤回",
          msg: `确定要撤回通知「${item.title}」吗？`,
          successText: "撤回成功",
          action: async () => {
            await NoticeAPI.revoke(Number(item.id));
            loadNoticeList();
          },
        }),
    });
  }

  showActions(menus);
}

onLoad(() => {
  loadNoticeList();
});
</script>

<script lang="ts">
export default { options: { styleIsolation: "shared" } };
</script>

<style lang="scss" scoped>
.notice-card__main {
  flex: 1;
}

.notice-card__title {
  font-size: 32rpx;
  font-weight: 700;
}

.notice-card__publisher {
  font-size: 24rpx;
  color: var(--color-text-secondary);
}

.notice-card__meta {
  display: flex;
  gap: 24rpx;
  margin-top: 12rpx;
}

.notice-card__detail {
  display: flex;
  align-items: flex-start;
  min-width: 0;
}

.notice-card__detail-text {
  margin-left: 8rpx;
  font-size: 24rpx;
  color: var(--color-text-secondary);
}

.notice-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16rpx;
}
</style>
