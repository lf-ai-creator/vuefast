<template>
  <el-card class="page-search codegen-search" shadow="never">
    <el-form ref="queryFormRef" :model="params" :inline="true">
      <el-form-item prop="keywords" label="关键字">
        <el-input
          v-model="params.keywords"
          placeholder="请输入表名"
          clearable
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleQuery">
          <template #icon><Search /></template>
          搜索
        </el-button>
        <el-button @click="handleResetQuery">
          <template #icon><Refresh /></template>
          重置
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>

  <el-card ref="tableWrapperRef" class="page-content codegen-table-card" shadow="never">
    <div class="page-toolbar">
      <div class="page-toolbar__left">
        <span class="codegen-table-title">数据表</span>
        <span class="codegen-table-meta">共 {{ total }} 张表</span>
      </div>
      <div class="page-toolbar__right">
        <el-tooltip content="刷新" placement="top">
          <el-button class="page-icon-btn" :loading="loading" @click="fetchData">
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
        v-loading="loading"
        :data="list"
        class="page-table"
        height="100%"
        highlight-current-row
        border
      >
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column label="表名" prop="tableName" min-width="180" />
        <el-table-column label="备注" prop="tableComment" min-width="260" show-overflow-tooltip />
        <el-table-column
          label="代码配置时间"
          align="center"
          prop="configTime"
          width="180"
          :formatter="(row, column, cellValue) => formatDateTime(cellValue)"
        />
        <el-table-column fixed="right" label="操作" width="300" align="center">
          <template #default="scope">
            <el-tag
              v-if="scope.row.isConfigured === TABLE_CONFIGURED"
              size="small"
              type="success"
              effect="plain"
              class="mr-2"
            >
              已配置
            </el-tag>
            <el-button
              type="primary"
              size="small"
              link
              @click="emit('configure', scope.row.tableName)"
            >
              <template #icon><Setting /></template>
              代码配置
            </el-button>
            <el-button
              type="primary"
              size="small"
              link
              @click="emit('preview', scope.row.tableName)"
            >
              <template #icon><View /></template>
              代码预览
            </el-button>
            <el-button
              type="primary"
              size="small"
              link
              @click="handleDownload(scope.row.tableName)"
            >
              <template #icon><Download /></template>
              下载
            </el-button>
            <el-button
              v-if="scope.row.isConfigured === TABLE_CONFIGURED"
              type="danger"
              size="small"
              link
              @click="emit('reset-config', scope.row.tableName)"
            >
              <template #icon><RefreshLeft /></template>
              重置配置
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
      class="page-pagination"
      @pagination="fetchData"
    />
  </el-card>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useFullscreen } from "@vueuse/core";
import {
  Download,
  FullScreen,
  Refresh,
  RefreshLeft,
  Search,
  Setting,
  View,
} from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox, type FormInstance } from "element-plus";

import GeneratorAPI from "@/api/codegen";
import type { TableItem, TableQueryParams } from "@/api/codegen";
import { usePageTable } from "@/composables";
import { formatDateTime } from "@/utils/format";

/** 表已配置代码生成（1:是;0:否）。 */
const TABLE_CONFIGURED = 1;

const emit = defineEmits<{
  configure: [tableName: string];
  preview: [tableName: string];
  "reset-config": [tableName: string];
}>();

const queryFormRef = ref<FormInstance>();
const tableWrapperRef = ref<HTMLElement | null>(null);
const { toggle: toggleFullscreen } = useFullscreen(tableWrapperRef);

// ── 分页表格状态 ────────────────────────────────────────────
/** 分页表格数据管理 */
const { loading, list, total, params, fetchData, handleQuery, handleResetQuery } = usePageTable<
  TableItem,
  TableQueryParams
>({
  initialParams: {
    pageNum: 1,
    pageSize: 10,
  },
  request: GeneratorAPI.getTablePage,
  onBeforeReset: () => queryFormRef.value?.resetFields(),
});

/**
 * 重置指定表的代码生成配置。
 *
 * @param tableName 表名
 */
async function handleResetConfig(tableName: string): Promise<void> {
  try {
    await ElMessageBox.confirm("确定要重置配置吗？", "提示", { type: "warning" });
  } catch {
    return;
  }

  await GeneratorAPI.resetGenConfig(tableName);
  ElMessage.success("重置成功");
  handleQuery();
}

async function handleDownload(tableName: string): Promise<void> {
  try {
    await GeneratorAPI.download(tableName, "classic");
    ElMessage.success("代码下载成功");
  } catch {
    ElMessage.error("代码下载失败，请先检查代码配置");
  }
}

onMounted(() => {
  handleQuery();
});

defineExpose({ handleQuery, handleResetConfig });
</script>

<style scoped lang="scss">
.codegen-search {
  :deep(.el-form-item) {
    margin-bottom: 0;
  }
}

.codegen-table-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.codegen-table-meta {
  margin-left: 10px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

@media (max-width: 768px) {
  .codegen-search {
    :deep(.el-input) {
      width: 100%;
    }
  }

  :deep(.codegen-table-card .el-table) {
    .el-table__cell:nth-child(4),
    .el-table__cell:nth-child(5) {
      display: none;
    }
  }
}
</style>
