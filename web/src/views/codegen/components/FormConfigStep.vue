<template>
  <div class="form-config-step">
    <section class="form-workbench">
      <div class="settings-panel">
        <div class="panel-title">
          <el-icon><EditPen /></el-icon>
          <span>新增、修改设置</span>
        </div>
        <el-form label-width="96px" class="settings-form">
          <el-form-item label="是否支持" required>
            <el-radio-group v-model="formData.formEnabled" @change="handleFormEnabledChange">
              <el-radio-button :value="1">支持</el-radio-button>
              <el-radio-button :value="0">不支持新增、修改</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="页面方式" required>
            <el-radio-group v-model="formData.formLayout" :disabled="!formEnabled">
              <el-radio-button value="dialog">弹窗</el-radio-button>
              <el-radio-button value="drawer">抽屉</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="页面宽度" required>
            <el-input
              v-model="formData.formWidth"
              :disabled="!formEnabled"
              placeholder="如：600px 或 80%"
            />
          </el-form-item>
          <el-form-item label="每行数量" required>
            <el-input-number
              v-model="formData.formColumns"
              :disabled="!formEnabled"
              :min="1"
              :max="4"
              controls-position="right"
            />
          </el-form-item>
          <p class="settings-tip">
            配置会同步到生成的 Web 表单；App 页面将复用新增、更新字段配置。
          </p>
        </el-form>
      </div>

      <div class="layout-preview">
        <div class="preview-heading">
          <div>
            <strong>
              {{
                formEnabled
                  ? formData.formLayout === "drawer"
                    ? "抽屉表单预览"
                    : "弹窗表单预览"
                  : "未启用表单"
              }}
            </strong>
            <span v-if="formEnabled">
              宽度 {{ normalizedWidth }} · 每行 {{ formColumns }} 个字段
            </span>
          </div>
          <el-tag :type="formEnabled ? 'success' : 'info'" effect="plain">
            {{ formEnabled ? "已启用" : "未启用" }}
          </el-tag>
        </div>
        <div v-if="formEnabled" class="preview-frame" :class="`is-${formData.formLayout}`">
          <div class="preview-bar">
            {{ formData.formLayout === "drawer" ? "新增 / 修改" : "新增业务数据" }}
          </div>
          <div
            class="preview-grid"
            :style="{ gridTemplateColumns: `repeat(${formColumns}, minmax(0, 1fr))` }"
          >
            <div v-for="field in previewFields" :key="field.columnName" class="preview-field">
              {{ field.fieldComment || field.columnComment || field.fieldName }}
            </div>
            <div v-if="!previewFields.length" class="preview-empty">请在下方选择新增或更新字段</div>
          </div>
          <div class="preview-actions">
            <span>取消</span>
            <b>确定</b>
          </div>
        </div>
        <el-empty v-else description="当前表不生成新增、修改表单" :image-size="78" />
      </div>
    </section>

    <el-alert
      title="“新增”和“更新”分别控制字段在创建、编辑表单中的显示；至少选择其中一项才会生成该字段。"
      type="info"
      :closable="false"
      show-icon
    />

    <el-table :data="fields" border class="config-table">
      <el-table-column label="列名" min-width="170">
        <template #default="{ row }">
          <div class="column-name">
            <div>
              <el-tag v-if="row.isPk" size="small" type="warning" effect="dark">主键</el-tag>
              <span class="font-mono">{{ row.columnName }}</span>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="列描述" prop="columnComment" min-width="170" show-overflow-tooltip />
      <el-table-column label="列类型" prop="columnType" width="130" />
      <el-table-column label="非空" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.isNullable === 'NO'" type="danger" effect="plain">非空</el-tag>
          <span v-else class="muted">可空</span>
        </template>
      </el-table-column>
      <el-table-column label="必填" width="78" align="center">
        <template #default="{ row }">
          <el-checkbox
            v-model="row.isRequired"
            :true-value="1"
            :false-value="0"
            :disabled="!formEnabled || !isVisibleInForm(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="新增" width="78" align="center">
        <template #default="{ row }">
          <el-checkbox
            v-model="row.isShowInCreate"
            :true-value="1"
            :false-value="0"
            :disabled="!formEnabled"
            @change="syncFormVisibility(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="更新" width="78" align="center">
        <template #default="{ row }">
          <el-checkbox
            v-model="row.isShowInUpdate"
            :true-value="1"
            :false-value="0"
            :disabled="!formEnabled"
            @change="syncFormVisibility(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="前端组件" min-width="180">
        <template #default="{ row }">
          <el-select v-model="row.formType" :disabled="!formEnabled || !isVisibleInForm(row)">
            <el-option
              v-for="item in formTypeOptions"
              :key="String(item.value)"
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
import type { FieldConfig, GenConfigForm } from "@/api/codegen";
import { FormTypeEnum } from "@/enums/codegen";

const formData = defineModel<GenConfigForm>({ required: true });
const fields = computed(() => formData.value.fieldConfigs || []);
const formTypeOptions = Object.values(FormTypeEnum);
const formEnabled = computed(() => formData.value.formEnabled !== 0);
const formColumns = computed(() => Math.min(Math.max(formData.value.formColumns || 2, 1), 4));
const normalizedWidth = computed(() => {
  const width = formData.value.formWidth?.trim() || "600px";
  return width.endsWith("px") || width.endsWith("%") ? width : `${width}px`;
});
const previewFields = computed(() => fields.value.filter(isVisibleInForm).slice(0, 12));

function isVisibleInForm(field: FieldConfig) {
  return field.isShowInCreate === 1 || field.isShowInUpdate === 1;
}

function syncFormVisibility(field: FieldConfig) {
  field.isShowInForm = isVisibleInForm(field) ? 1 : 0;
  if (!field.isShowInForm) field.isRequired = 0;
}

function handleFormEnabledChange(enabled: string | number | boolean | undefined) {
  if (Number(enabled) !== 0) {
    fields.value.forEach(syncFormVisibility);
    return;
  }
  fields.value.forEach((field) => {
    field.isShowInForm = 0;
    field.isRequired = 0;
  });
}
</script>

<style scoped lang="scss">
.form-config-step {
  display: grid;
  gap: 16px;
}
.form-workbench {
  display: grid;
  grid-template-columns: minmax(310px, 0.68fr) minmax(460px, 1.32fr);
  overflow: hidden;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
}
.settings-panel {
  padding: 20px;
  border-right: 1px solid var(--el-border-color-lighter);
}
.panel-title {
  display: flex;
  gap: 8px;
  align-items: center;
  padding-bottom: 14px;
  margin-bottom: 16px;
  font-weight: 600;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.panel-title .el-icon {
  color: var(--el-color-primary);
}
.settings-form :deep(.el-form-item) {
  margin-bottom: 16px;
}
.settings-form :deep(.el-input),
.settings-form :deep(.el-input-number) {
  width: 100%;
}
.settings-tip {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--el-text-color-secondary);
}
.layout-preview {
  padding: 20px;
  background: var(--el-fill-color-extra-light);
}
.preview-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.preview-heading > div {
  display: grid;
  gap: 4px;
}
.preview-heading span {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.preview-frame {
  min-height: 210px;
  padding: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-lighter);
}
.preview-frame.is-drawer {
  width: 72%;
  margin-left: auto;
  border-radius: 8px 0 0 8px;
}
.preview-bar {
  padding-bottom: 12px;
  margin-bottom: 14px;
  font-weight: 600;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.preview-grid {
  display: grid;
  gap: 10px;
}
.preview-field {
  min-height: 34px;
  padding: 8px 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
  color: #fff;
  white-space: nowrap;
  background: var(--el-color-primary-light-3);
  border-radius: 4px;
}
.preview-empty {
  grid-column: 1 / -1;
  padding: 42px;
  color: var(--el-text-color-secondary);
  text-align: center;
  border: 1px dashed var(--el-border-color);
  border-radius: 4px;
}
.preview-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 16px;
  margin-top: 16px;
  font-size: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}
.preview-actions b {
  padding: 3px 11px;
  font-weight: 400;
  color: #fff;
  background: var(--el-color-primary);
  border-radius: 3px;
}
.config-table {
  border-radius: 10px;
}
.column-name > div {
  display: flex;
  gap: 8px;
  align-items: center;
}
.muted {
  color: var(--el-text-color-secondary);
}
@media (max-width: 1000px) {
  .form-workbench {
    grid-template-columns: 1fr;
  }
  .settings-panel {
    border-right: 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }
}
@media (max-width: 768px) {
  .settings-panel,
  .layout-preview {
    padding: 14px;
  }
  .preview-frame.is-drawer {
    width: 88%;
  }
}
</style>
