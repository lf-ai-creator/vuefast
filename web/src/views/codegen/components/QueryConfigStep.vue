<template>
  <div class="step-panel">
    <div class="step-toolbar">
      <el-alert
        title="仅启用的字段会生成查询控件；日期字段建议使用 BETWEEN。"
        type="success"
        :closable="false"
        show-icon
      />
      <el-button type="primary" plain @click="enableRecommended">应用推荐配置</el-button>
    </div>
    <el-table :data="fields" border class="config-table">
      <el-table-column label="查询条件" width="100" align="center">
        <template #default="{ row }">
          <el-switch v-model="row.isShowInQuery" :active-value="1" :inactive-value="0" />
        </template>
      </el-table-column>
      <el-table-column label="查询列" prop="columnName" min-width="180" />
      <el-table-column label="条件名称" min-width="200">
        <template #default="{ row }"><el-input v-model="row.queryName" /></template>
      </el-table-column>
      <el-table-column label="字段命名" prop="fieldName" min-width="180" />
      <el-table-column label="查询方式" min-width="190">
        <template #default="{ row }">
          <el-select v-model="row.queryType" :disabled="row.isShowInQuery !== 1">
            <el-option
              v-for="item in queryTypeOptions"
              :key="String(item.value)"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="查询组件" min-width="170">
        <template #default="{ row }">
          <el-tag effect="plain" :type="row.isShowInQuery === 1 ? 'primary' : 'info'">
            {{ componentLabel(row.formType) }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import type { GenConfigForm } from "@/api/codegen";
import { FormTypeEnum, QueryTypeEnum } from "@/enums/codegen";

const formData = defineModel<GenConfigForm>({ required: true });
const fields = computed(() => formData.value.fieldConfigs || []);
const queryTypeOptions = Object.values(QueryTypeEnum);

function componentLabel(value?: number) {
  return Object.values(FormTypeEnum).find((item) => item.value === value)?.label || "输入框";
}

function enableRecommended() {
  fields.value.forEach((row) => {
    const name = row.fieldName || row.columnName || "";
    const systemField = ["id", "is_deleted", "create_time", "update_time"].includes(
      row.columnName || ""
    );
    row.isShowInQuery = systemField ? 0 : 1;
    if (/date|time/i.test(name)) row.queryType = QueryTypeEnum.BETWEEN.value as number;
    else if (row.fieldType === "str") row.queryType = QueryTypeEnum.LIKE.value as number;
    else row.queryType = QueryTypeEnum.EQ.value as number;
  });
}
</script>

<style scoped lang="scss">
.step-panel {
  display: grid;
  gap: 16px;
}
.step-toolbar {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  align-items: center;
}
.config-table {
  border-radius: 10px;
}
@media (max-width: 768px) {
  .step-toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
