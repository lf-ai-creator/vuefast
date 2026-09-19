<template>
  <div class="step-panel">
    <el-alert title="列表字段名称、列宽和自动省略仅作用于列表展示，不会影响查询条件与表单。" type="success" :closable="false" show-icon />
    <el-table :data="fields" border class="config-table">
      <el-table-column type="index" label="序号" width="70" align="center" />
      <el-table-column label="列名" prop="columnName" min-width="170" />
      <el-table-column label="列描述" prop="columnComment" min-width="170" />
      <el-table-column label="显示" width="80" align="center">
        <template #default="{ row }">
          <el-checkbox v-model="row.isShowInList" :true-value="1" :false-value="0" />
        </template>
      </el-table-column>
      <el-table-column label="字段名词" min-width="190">
        <template #default="{ row }">
          <el-input v-model="row.listName" :placeholder="row.columnComment || '使用列描述'" />
        </template>
      </el-table-column>
      <el-table-column label="字段命名" min-width="190">
        <template #default="{ row }"><el-input v-model="row.fieldName" /></template>
      </el-table-column>
      <el-table-column label="宽度" width="120">
        <template #default="{ row }">
          <el-input-number v-model="row.listWidth" :min="60" :max="600" :controls="false" placeholder="自动" class="width-input" />
        </template>
      </el-table-column>
      <el-table-column label="ellipsis" width="130" align="center">
        <template #default="{ row }">
          <el-switch v-model="row.listEllipsis" :active-value="1" :inactive-value="0" active-text="自动省略" inline-prompt />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import type { GenConfigForm } from "@/api/codegen";

const formData = defineModel<GenConfigForm>({ required: true });
const fields = computed(() => formData.value.fieldConfigs || []);
</script>

<style scoped lang="scss">
.step-panel { display: grid; gap: 16px; }
.config-table { border-radius: 10px; }
.width-input { width: 100%; }
.width-input :deep(.el-input__inner) { text-align: left; }
</style>
