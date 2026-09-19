<template>
  <div class="page-container">
    <el-card class="page-search" shadow="never">
      <el-form ref="queryFormRef" :model="params" :inline="true">
        <el-form-item label="通知标题" prop="title">
          <el-input
            v-model="params.title"
            placeholder="关键字"
            clearable
            @keyup.enter="handleQuery"
          />
        </el-form-item>

        <el-form-item label="阅读状态" prop="isRead">
          <el-select v-model="params.isRead" clearable placeholder="全部状态" style="width: 130px">
            <el-option label="未读" :value="NOTICE_UNREAD" />
            <el-option label="已读" :value="NOTICE_READ" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleQuery">
            <template #icon>
              <Search />
            </template>
            搜索
          </el-button>
          <el-button @click="handleResetQuery">
            <template #icon>
              <Refresh />
            </template>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="page-content" shadow="never">
      <div class="notice-toolbar">
        <div class="notice-toolbar__summary">
          <span class="notice-toolbar__title">我的通知</span>
          <el-tag v-if="unreadCount > 0" type="danger" effect="light" round>
            {{ unreadCount }} 条未读
          </el-tag>
          <span v-else class="notice-toolbar__hint">暂无未读通知</span>
        </div>
        <el-button
          type="primary"
          plain
          :icon="Check"
          :loading="readAllLoading"
          :disabled="unreadCount === 0"
          @click="handleReadAll"
        >
          全部已读
        </el-button>
      </div>

      <div class="page-table-wrapper">
        <el-table
          v-loading="loading"
          :data="list"
          class="page-table"
          height="100%"
          highlight-current-row
        >
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column label="通知标题" prop="title" min-width="200" />
          <el-table-column align="center" label="通知类型" width="150">
            <template #default="scope">
              <DictTag v-model="scope.row.type" code="notice_type" />
            </template>
          </el-table-column>
          <el-table-column align="center" label="通知等级" width="100">
            <template #default="scope">
              <DictTag v-model="scope.row.level" code="notice_level" />
            </template>
          </el-table-column>
          <el-table-column
            key="releaseTime"
            align="center"
            label="发布时间"
            prop="publishTime"
            :formatter="(row, column, cellValue) => formatDateTime(cellValue)"
            width="150"
          />
          <el-table-column align="center" label="发布人" prop="publisherName" width="150" />
          <el-table-column align="center" label="状态" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.isRead === NOTICE_READ" type="success">已读</el-tag>
              <el-tag v-else type="info">未读</el-tag>
            </template>
          </el-table-column>
          <el-table-column align="center" fixed="right" label="操作" width="80">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                link
                :loading="readingId === scope.row.id"
                @click="handleReadNotice(scope.row as NoticeItem)"
              >
                查看
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

    <NoticeDetailDialog v-model="noticeDialogVisible" :detail="noticeDetail" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { Check, Refresh, Search } from "@element-plus/icons-vue";

import NoticeAPI from "@/api/system/notice";
import type { NoticeDetail, NoticeItem, NoticeQueryParams } from "@/api/system/notice";
import { usePageTable } from "@/composables";
import { formatDateTime } from "@/utils/format";

defineOptions({
  name: "MyNotice",
  inheritAttrs: false,
});

/** 通知已读标记（1:已读;0:未读）。 */
const NOTICE_UNREAD = 0;
const NOTICE_READ = 1;

const queryFormRef = ref();

/** 分页表格数据管理 */
const { loading, list, total, params, fetchData, handleQuery, handleResetQuery } = usePageTable<
  NoticeItem,
  NoticeQueryParams
>({
  initialParams: {
    pageNum: 1,
    pageSize: 10,
  },
  request: NoticeAPI.getMyNoticePage,
  onBeforeReset: () => queryFormRef.value?.resetFields(),
});

const noticeDialogVisible = ref(false);
const noticeDetail = ref<NoticeDetail | null>(null);
const readingId = ref<string | null>(null);
const readAllLoading = ref(false);

const unreadCount = computed(
  () => list.value.filter((item) => item.isRead === NOTICE_UNREAD).length
);

/**
 * 查看通知详情。
 *
 * @param id 通知 ID
 */
async function handleReadNotice(row: NoticeItem): Promise<void> {
  readingId.value = row.id;
  try {
    const data = await NoticeAPI.getDetail(row.id);
    noticeDetail.value = data;
    noticeDialogVisible.value = true;
    row.isRead = NOTICE_READ;
  } finally {
    readingId.value = null;
  }
}

async function handleReadAll(): Promise<void> {
  if (!unreadCount.value) return;
  readAllLoading.value = true;
  try {
    await NoticeAPI.readAll();
    list.value.forEach((item) => {
      item.isRead = NOTICE_READ;
    });
    ElMessage.success("全部通知已读");
  } finally {
    readAllLoading.value = false;
  }
}

onMounted(() => {
  handleQuery();
});
</script>

<style lang="scss" scoped>
.notice-toolbar {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: space-between;
  min-height: 32px;
  margin-bottom: 10px;
}

.notice-toolbar__summary {
  display: flex;
  gap: 10px;
  align-items: center;
  min-width: 0;
}

.notice-toolbar__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.notice-toolbar__hint {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

@media (max-width: 600px) {
  .notice-toolbar {
    align-items: flex-start;
    gap: 8px;
  }

  .notice-toolbar__summary {
    flex-wrap: wrap;
    gap: 6px;
  }
}
</style>
