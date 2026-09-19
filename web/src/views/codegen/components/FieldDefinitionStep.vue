<template>
  <div class="step-panel">
    <el-alert
      title="字段命名将同时影响 FastAPI Schema、SQLAlchemy Model、Web 与 App 类型，请确保名称完整且唯一。"
      type="success"
      :closable="false"
      show-icon
    />

    <el-table :data="fields" border class="config-table">
      <el-table-column label="列名" prop="columnName" min-width="180">
        <template #default="{ row }">
          <div class="field-name-cell">
            <div>
              <el-tag v-if="row.isPk" size="small" type="warning" effect="dark">主键</el-tag>
              <span class="font-mono">{{ row.columnName }}</span>
            </div>
            <span class="column-meta">{{ row.columnType }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="列描述" min-width="180">
        <template #default="{ row }">
          <span class="readonly-text">{{ row.columnComment || "-" }}</span>
        </template>
      </el-table-column>
      <el-table-column label="非空" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.isNullable === 'NO'" type="danger" effect="plain">非空</el-tag>
          <span v-else class="muted">可空</span>
        </template>
      </el-table-column>
      <el-table-column label="字段命名" min-width="180">
        <template #default="{ row }">
          <el-input v-model="row.fieldName" placeholder="默认小驼峰，如 userName" />
        </template>
      </el-table-column>
      <el-table-column label="字段名词" min-width="180">
        <template #default="{ row }">
          <el-input v-model="row.fieldComment" placeholder="用于生成代码注释" />
        </template>
      </el-table-column>
      <el-table-column label="Python 类型" min-width="150">
        <template #default="{ row }">
          <el-select v-model="row.fieldType" filterable>
            <el-option v-for="item in pythonTypes" :key="item" :label="item" :value="item" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="前端类型" min-width="170">
        <template #default="{ row }">
          <el-select v-model="row.frontendType" filterable>
            <el-option v-for="type in frontendTypes" :key="type" :label="type" :value="type" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="字典" min-width="170">
        <template #default="{ row }">
          <el-select v-model="row.dictType" clearable filterable placeholder="请选择字典">
            <el-option
              v-for="item in dictOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import type { GenConfigForm } from "@/api/codegen";
import type { OptionItem } from "@/api/common";

const formData = defineModel<GenConfigForm>({ required: true });
defineProps<{ dictOptions?: OptionItem[] }>();

const pythonTypes = ["str", "int", "float", "Decimal", "bool", "datetime", "date", "time", "dict"];
const frontendTypes = [
  "string",
  "number",
  "boolean",
  "Date",
  "string[]",
  "number[]",
  "Record<string, any>",
  "any",
];
const fields = computed(() => formData.value.fieldConfigs || []);
</script>

<style scoped lang="scss">
.step-panel {
  display: grid;
  gap: 16px;
}
.config-table {
  border-radius: 10px;
}
.field-name-cell {
  display: grid;
  gap: 6px;
}
.field-name-cell > div {
  display: flex;
  gap: 8px;
  align-items: center;
}
.column-meta,
.muted {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.readonly-text {
  color: var(--el-text-color-regular);
}
</style>
