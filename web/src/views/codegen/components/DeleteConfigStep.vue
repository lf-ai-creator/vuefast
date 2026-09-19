<template>
  <div class="delete-step">
    <div class="table-summary">
      <div class="summary-item"><span>数据库表名词：</span><code>{{ formData.tableName || "-" }}</code></div>
      <div class="summary-item"><span>数据库表备注：</span><span>{{ formData.businessName || "未填写" }}</span></div>
    </div>

    <el-form class="delete-form" label-width="150px">
      <el-form-item label="是否允许删除：" required>
        <el-radio-group v-model="formData.deleteEnabled">
          <el-radio-button :value="1">支持删除</el-radio-button>
          <el-radio-button :value="0">不允许删除</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <template v-if="formData.deleteEnabled !== 0">
        <el-form-item label="是否为物理删除：" required>
          <el-radio-group v-model="formData.deleteMode">
            <el-radio-button value="physical">物理删除</el-radio-button>
            <el-radio-button value="logical">假删</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <p v-if="formData.deleteMode !== 'physical'" class="soft-delete-field">
          假删字段为：<code>{{ softDeleteField?.columnName || "is_deleted（基础模型字段）" }}</code>
        </p>

        <el-form-item label="删除类型：" required>
          <el-select v-model="formData.deleteType" class="delete-type-select">
            <el-option label="单个删除和批量删除" value="single_batch" />
            <el-option label="仅单个删除" value="single" />
            <el-option label="仅批量删除" value="batch" />
          </el-select>
        </el-form-item>
      </template>
    </el-form>

    <el-alert
      type="info"
      :closable="false"
      show-icon
      title="删除配置将作为生成策略保存；逻辑删除默认复用项目基础模型的删除标记。"
    />
  </div>
</template>

<script setup lang="ts">
import type { GenConfigForm } from "@/api/codegen";

const formData = defineModel<GenConfigForm>({ required: true });
const softDeleteField = computed(() =>
  formData.value.fieldConfigs?.find((item) => ["is_deleted", "deleted_flag"].includes(item.columnName || ""))
);
</script>

<style scoped lang="scss">
.delete-step { max-width: 920px; padding: 12px 24px; margin: 0 auto; }
.table-summary { display: grid; gap: 28px; padding: 18px 24px 36px; font-size: 16px; line-height: 1.6; }
.summary-item { display: flex; gap: 10px; align-items: baseline; }
.summary-item > span:first-child { min-width: 112px; color: var(--el-text-color-primary); }
code { padding: 1px 5px; color: var(--el-text-color-primary); background: var(--el-fill-color-light); border-radius: 4px; }
.delete-form { padding: 12px 24px 10px; }
.delete-form :deep(.el-form-item) { margin-bottom: 26px; }
.delete-form :deep(.el-form-item__label) { font-weight: 500; }
.delete-form :deep(.el-radio-button__inner) { min-width: 120px; }
.soft-delete-field { margin: -12px 0 26px 150px; color: var(--el-text-color-regular); }
.delete-type-select { width: 310px; }
@media (max-width: 640px) { .delete-step { padding: 8px; } .table-summary, .delete-form { padding-inline: 0; } .soft-delete-field { margin-left: 0; } }
</style>
