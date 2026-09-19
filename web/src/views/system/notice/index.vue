<template>
  <div class="page-container">
    <el-card class="page-search" shadow="never">
      <el-form ref="queryFormRef" :model="params" :inline="true" label-suffix=":">
        <el-form-item label="标题" prop="title">
          <el-input
            v-model="params.title"
            placeholder="标题"
            clearable
            @keyup.enter="handleQuery()"
          />
        </el-form-item>

        <el-form-item label="发布状态" prop="publishStatus">
          <el-select
            v-model="params.publishStatus"
            clearable
            placeholder="全部"
            style="width: 100px"
          >
            <el-option :value="NOTICE_STATUS_DRAFT" label="未发布" />
            <el-option :value="NOTICE_STATUS_PUBLISHED" label="已发布" />
            <el-option :value="NOTICE_STATUS_REVOKED" label="已撤回" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleQuery()">搜索</el-button>
          <el-button @click="handleResetQuery()">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card ref="tableWrapperRef" class="page-content" shadow="never">
      <div class="page-toolbar">
        <div class="page-toolbar__left">
          <el-button v-hasPerm="['sys:notice:create']" type="primary" @click="openDialog()">
            新增通知
          </el-button>
          <el-button
            v-hasPerm="['sys:notice:delete']"
            type="danger"
            :disabled="!hasSelection"
            @click="handleDelete()"
          >
            删除
          </el-button>
        </div>
        <div class="page-toolbar__right">
          <el-tooltip content="刷新" placement="top">
            <el-button class="page-icon-btn" @click="fetchData">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="全屏" placement="top">
            <el-button class="page-icon-btn" @click="toggleFullscreen">
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
      </div>

      <div class="page-table-wrapper">
        <el-table
          ref="dataTableRef"
          v-loading="loading"
          :data="list"
          class="page-table"
          border
          height="100%"
          highlight-current-row
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column
            label="通知标题"
            prop="title"
            min-width="220"
            header-align="center"
            show-overflow-tooltip
          />
          <el-table-column align="center" label="通知类型" width="150">
            <template #default="scope">
              <DictTag v-model="scope.row.type" :code="'notice_type'" />
            </template>
          </el-table-column>
          <el-table-column align="center" label="发布人" prop="publisherName" width="150" />
          <el-table-column align="center" label="通知等级" width="100">
            <template #default="scope">
              <DictTag v-model="scope.row.level" code="notice_level" />
            </template>
          </el-table-column>
          <el-table-column align="center" label="接收范围" prop="targetType" width="110">
            <template #default="scope">
              <el-tag v-if="scope.row.targetType === NOTICE_TARGET_ALL" type="warning">全体</el-tag>
              <el-tag v-if="scope.row.targetType === NOTICE_TARGET_SPECIFIED" type="success">
                指定
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column align="center" label="发布状态" min-width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.publishStatus === NOTICE_STATUS_DRAFT" type="info">
                未发布
              </el-tag>
              <el-tag
                v-else-if="scope.row.publishStatus === NOTICE_STATUS_PUBLISHED"
                type="success"
              >
                已发布
              </el-tag>
              <el-tag v-else-if="scope.row.publishStatus === NOTICE_STATUS_REVOKED" type="warning">
                已撤回
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作时间" min-width="245" header-align="center">
            <template #default="scope">
              <div class="notice-time">
                <span class="notice-time__label">创建</span>
                <span>{{ formatNoticeTime(scope.row.createTime) }}</span>
              </div>

              <div v-if="scope.row.publishStatus === NOTICE_STATUS_PUBLISHED" class="notice-time">
                <span class="notice-time__label">发布</span>
                <span>{{ formatNoticeTime(scope.row.publishTime) }}</span>
              </div>
              <div
                v-else-if="scope.row.publishStatus === NOTICE_STATUS_REVOKED"
                class="notice-time"
              >
                <span class="notice-time__label">撤回</span>
                <span>{{ formatNoticeTime(scope.row.revokeTime) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column align="center" fixed="right" label="操作" width="200">
            <template #default="scope">
              <el-button type="primary" size="small" link @click="openDetailDialog(scope.row.id)">
                查看
              </el-button>
              <el-button
                v-if="scope.row.publishStatus !== NOTICE_STATUS_PUBLISHED"
                v-hasPerm="['sys:notice:publish']"
                type="primary"
                size="small"
                link
                @click="handlePublish(scope.row.id)"
              >
                发布
              </el-button>
              <el-button
                v-if="scope.row.publishStatus === NOTICE_STATUS_PUBLISHED"
                v-hasPerm="['sys:notice:revoke']"
                type="primary"
                size="small"
                link
                @click="handleRevoke(scope.row.id)"
              >
                撤回
              </el-button>
              <el-button
                v-if="scope.row.publishStatus !== NOTICE_STATUS_PUBLISHED"
                v-hasPerm="['sys:notice:update']"
                type="primary"
                size="small"
                link
                @click="openDialog(scope.row.id)"
              >
                编辑
              </el-button>
              <el-button
                v-if="scope.row.publishStatus !== NOTICE_STATUS_PUBLISHED"
                v-hasPerm="['sys:notice:delete']"
                type="danger"
                size="small"
                link
                @click="handleDelete(scope.row.id)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <pagination
        v-if="total > 0"
        v-model:total="total"
        v-model:page="params.pageNum"
        v-model:limit="params.pageSize"
        @pagination="fetchData"
      />
    </el-card>

    <el-dialog
      v-model="dialogState.visible"
      :show-close="true"
      :fullscreen="dialogState.fullscreen"
      class="notice-form-dialog"
      top="5vh"
      width="820px"
      append-to-body
      @close="closeDialog"
    >
      <template #header>
        <div class="notice-form-dialog__header">
          <span class="notice-form-dialog__title">{{ dialogState.title }}</span>
          <el-tooltip
            :content="dialogState.fullscreen ? '退出全屏' : '全屏显示'"
            placement="bottom"
          >
            <el-button
              class="notice-form-dialog__fullscreen"
              text
              circle
              :aria-label="dialogState.fullscreen ? '退出全屏' : '全屏显示'"
              @click="toggleDialogFullscreen"
            >
              <template #icon>
                <FullScreen v-if="!dialogState.fullscreen" />
                <CopyDocument v-else />
              </template>
            </el-button>
          </el-tooltip>
        </div>
      </template>
      <div class="notice-form-dialog__scroll">
        <el-form
          ref="noticeFormRef"
          class="notice-form"
          :model="formData"
          :rules="rules"
          label-position="top"
        >
          <el-form-item class="notice-form__full" label="通知标题" prop="title">
            <el-input
              v-model="formData.title"
              maxlength="100"
              placeholder="请输入通知标题"
              show-word-limit
              clearable
            />
          </el-form-item>

          <el-form-item label="通知类型" prop="type">
            <DictSelect v-model="formData.type" code="notice_type" />
          </el-form-item>
          <el-form-item label="通知等级" prop="level">
            <DictSelect v-model="formData.level" code="notice_level" />
          </el-form-item>
          <el-form-item class="notice-form__full" label="接收范围" prop="targetType">
            <el-radio-group v-model="formData.targetType">
              <el-radio :value="NOTICE_TARGET_ALL">全体用户</el-radio>
              <el-radio :value="NOTICE_TARGET_SPECIFIED">指定用户</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item
            v-if="formData.targetType === NOTICE_TARGET_SPECIFIED"
            class="notice-form__full"
            label="指定用户"
            prop="targetUsers"
          >
            <el-select
              v-model="formData.targetUsers"
              multiple
              filterable
              collapse-tags
              collapse-tags-tooltip
              placeholder="请选择接收用户"
            >
              <el-option
                v-for="item in userOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item
            class="notice-form__full notice-form__content"
            label="通知内容"
            prop="content"
          >
            <WangEditor v-model="formData.content" height="320px" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="handleSubmit()">确定</el-button>
          <el-button @click="closeDialog()">取消</el-button>
        </div>
      </template>
    </el-dialog>
    <NoticeDetailDialog v-model="detailDialog.visible" :detail="currentNotice" />
  </div>
</template>

<script setup lang="ts">
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";
import { CopyDocument, FullScreen, Refresh } from "@element-plus/icons-vue";

import NoticeAPI from "@/api/system/notice";
import type { NoticeDetail, NoticeForm, NoticeItem, NoticeQueryParams } from "@/api/system/notice";
import UserAPI from "@/api/system/user";
import type { OptionItem } from "@/api/common";
import { usePageTable, useTableSelection } from "@/composables";
import { formatDateTime } from "@/utils/format";

defineOptions({
  name: "Notice",
  inheritAttrs: false,
});

const tableWrapperRef = ref<HTMLElement | null>(null);
const { toggle: toggleFullscreen } = useFullscreen(tableWrapperRef);

const queryFormRef = ref<FormInstance>();
const noticeFormRef = ref<FormInstance>();

// 通知发布状态：0=未发布，1=已发布，-1=已撤回。
const NOTICE_STATUS_DRAFT = 0;
const NOTICE_STATUS_PUBLISHED = 1;
const NOTICE_STATUS_REVOKED = -1;
/** 通知目标类型：1=全体，2=指定用户。 */
const NOTICE_TARGET_ALL = 1;
const NOTICE_TARGET_SPECIFIED = 2;

function formatNoticeTime(value?: string | Date | null): string {
  if (!value) return "-";
  return formatDateTime(value) || "-";
}

/** 分页表格数据管理 */
const { loading, list, total, params, fetchData, handleQuery, handleResetQuery } = usePageTable<
  NoticeItem,
  NoticeQueryParams
>({
  initialParams: {
    pageNum: 1,
    pageSize: 10,
    title: "",
    publishStatus: undefined,
  },
  request: NoticeAPI.getPage,
  onBeforeReset: () => queryFormRef.value?.resetFields(),
});

const { selectedIds, hasSelection, handleSelectionChange } = useTableSelection<NoticeItem>();

const userOptions = ref<OptionItem[]>([]);

const dialogState = reactive({
  title: "",
  visible: false,
  fullscreen: false,
});

const initialFormData: NoticeForm = {
  level: "L",
  targetType: NOTICE_TARGET_ALL,
};

const formData = reactive<NoticeForm>({ ...initialFormData });

const rules: FormRules<NoticeForm> = {
  title: [{ required: true, message: "请输入通知标题", trigger: "blur" }],
  content: [
    {
      required: true,
      message: "请输入通知内容",
      trigger: "blur",
      validator: (rule, value: string, callback) => {
        if (!value.replace(/<[^>]+>/g, "").trim()) {
          callback(new Error("请输入通知内容"));
        } else {
          callback();
        }
      },
    },
  ],
  type: [{ required: true, message: "请选择通知类型", trigger: "change" }],
};

const detailDialog = reactive({
  visible: false,
});
const currentNotice = ref<NoticeDetail>({});

/**
 * 将后端返回的 `targetUserIds`（可能是数组、JSON 字符串、逗号分隔字符串）标准化为数字数组。
 *
 * 用于编辑回显时把后端字段转换成表单 `targetUsers` 字段。
 *
 * @param value 后端返回的原始值
 */
function normalizeTargetUsers(value?: unknown): number[] {
  if (!value) {
    return [];
  }
  const toNumberArray = (arr: unknown[]): number[] =>
    arr.map((v) => Number(v)).filter((v) => Number.isFinite(v));
  if (Array.isArray(value)) {
    return toNumberArray(value);
  }
  if (typeof value === "string") {
    try {
      const parsed = JSON.parse(value);
      if (Array.isArray(parsed)) {
        return toNumberArray(parsed);
      }
      return value
        .split(",")
        .filter(Boolean)
        .map((v) => Number(v))
        .filter((v) => Number.isFinite(v));
    } catch {
      return value
        .split(",")
        .filter(Boolean)
        .map((v) => Number(v))
        .filter((v) => Number.isFinite(v));
    }
  }
  return [];
}

/**
 * 构造提交给后端的 payload。
 *
 * 字段名转换：targetUsers → targetUserIds。
 */
function buildSubmitPayload(): Omit<NoticeForm, "targetUsers"> & { targetUserIds: number[] } {
  const { targetUsers, ...rest } = formData;
  return {
    ...rest,
    targetUserIds: formData.targetType === NOTICE_TARGET_SPECIFIED ? (targetUsers ?? []) : [],
  };
}

/**
 * 重置表单数据和验证状态。
 *
 * 重置表单数据。
 */
function resetForm(): void {
  noticeFormRef.value?.resetFields();
  noticeFormRef.value?.clearValidate();
  Object.keys(formData).forEach((key) => {
    delete (formData as Record<string, unknown>)[key];
  });
  Object.assign(formData, initialFormData);
}

/**
 * 切换表单弹窗的全屏状态。
 */
function toggleDialogFullscreen(): void {
  dialogState.fullscreen = !dialogState.fullscreen;
}

/**
 * 打开新增/编辑通知弹窗。
 * @param id 通知 ID（编辑时传入）
 */
async function openDialog(id?: string): Promise<void> {
  dialogState.fullscreen = false;
  // 用户选项与弹窗并行加载
  UserAPI.getOptions().then((data) => {
    userOptions.value = data;
  });

  dialogState.visible = true;
  if (id) {
    dialogState.title = "修改公告";
    const data = await NoticeAPI.getFormData(id);
    Object.assign(formData, {
      ...data,
      targetUsers: normalizeTargetUsers(data.targetUsers),
    });
  } else {
    resetForm();
    dialogState.title = "新增公告";
  }
}

/**
 * 关闭表单弹窗并重置表单。
 */
function closeDialog(): void {
  dialogState.visible = false;
  dialogState.fullscreen = false;
  resetForm();
}

/**
 * 校验并提交通知表单
 */
async function handleSubmit(): Promise<void> {
  const valid = await noticeFormRef.value?.validate().then(
    () => true,
    () => false
  );
  if (!valid) return;

  loading.value = true;
  try {
    const payload = buildSubmitPayload();
    const id = formData.id;
    if (id) {
      await NoticeAPI.update(id, payload);
      ElMessage.success("修改成功");
    } else {
      await NoticeAPI.create(payload);
      ElMessage.success("新增成功");
    }
    closeDialog();
    handleResetQuery();
  } finally {
    loading.value = false;
  }
}

/**
 * 发布通知公告。
 *
 * @param id 通知 ID
 */
async function handlePublish(id: string): Promise<void> {
  await NoticeAPI.publish(id);
  ElMessage.success("发布成功");
  fetchData();
}

/**
 * 撤回通知公告。
 *
 * @param id 通知 ID
 */
async function handleRevoke(id: string): Promise<void> {
  await NoticeAPI.revoke(id);
  ElMessage.success("撤回成功");
  fetchData();
}

/**
 * 删除单个或批量通知。
 *
 * @param id 指定时删除单个通知；不指定时删除表格勾选项
 */
async function handleDelete(id?: string): Promise<void> {
  const deleteIds = id ?? selectedIds.value.join(",");
  if (!deleteIds) {
    ElMessage.warning("请勾选删除项");
    return;
  }

  try {
    await ElMessageBox.confirm("确认删除已选中的数据项吗？", "警告", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
  } catch {
    ElMessage.info("已取消删除");
    return;
  }

  loading.value = true;
  try {
    await NoticeAPI.deleteByIds(deleteIds);
    ElMessage.success("删除成功");
    handleResetQuery();
  } finally {
    loading.value = false;
  }
}

/**
 * 打开通知详情弹窗。
 *
 * @param id 通知 ID
 */
async function openDetailDialog(id: string): Promise<void> {
  currentNotice.value = await NoticeAPI.getDetail(id);
  detailDialog.visible = true;
}

onMounted(() => {
  handleQuery();
});
</script>

<style lang="scss" scoped>
.notice-form-dialog__scroll {
  max-height: calc(90vh - 132px);
  padding: 20px 24px 4px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.notice-form-dialog__header {
  display: flex;
  align-items: center;
  width: 100%;
  min-height: 24px;
}

.notice-form-dialog__title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: var(--el-dialog-title-font-size);
  line-height: var(--el-dialog-font-line-height);
  color: var(--el-text-color-primary);
  white-space: nowrap;
}

.notice-form-dialog__fullscreen {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  padding: 0;
  margin: -4px 0 -4px auto !important;
  font-size: var(--el-message-close-size, 16px);
  color: var(--el-text-color-secondary);

  &:hover {
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }
}

.notice-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 20px;

  &__full {
    grid-column: 1 / -1;
  }

  :deep(.el-form-item) {
    margin-bottom: 18px;
  }

  :deep(.el-form-item__label) {
    height: auto;
    padding-bottom: 7px;
    font-weight: 500;
    line-height: 20px;
    color: var(--el-text-color-primary);
  }

  :deep(.el-select) {
    width: 100%;
  }

  &__content {
    min-width: 0;
    margin-bottom: 10px !important;
  }
}

:global(.notice-form-dialog) {
  max-width: calc(100vw - 32px);
  overflow: hidden;
}

:global(.notice-form-dialog .el-dialog__body) {
  padding: 0;
}

:global(.notice-form-dialog.is-fullscreen) {
  display: flex;
  flex-direction: column;
  max-width: none;
  height: 100vh;
}

:global(.notice-form-dialog.is-fullscreen .el-dialog__header),
:global(.notice-form-dialog.is-fullscreen .el-dialog__footer) {
  flex-shrink: 0;
}

:global(.notice-form-dialog.is-fullscreen .el-dialog__body) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

:global(.notice-form-dialog.is-fullscreen .notice-form-dialog__scroll) {
  box-sizing: border-box;
  height: 100%;
  max-height: none;
}

@media (max-width: 600px) {
  .notice-form-dialog__scroll {
    padding: 16px 16px 2px;
  }

  .notice-form {
    grid-template-columns: minmax(0, 1fr);

    &__full {
      grid-column: auto;
    }
  }
}

.notice-time {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 13px;
  font-variant-numeric: tabular-nums;
  line-height: 22px;
  white-space: nowrap;

  &__label {
    flex-shrink: 0;
    color: var(--el-text-color-secondary);
  }
}
</style>
