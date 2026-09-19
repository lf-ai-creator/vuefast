<template>
  <el-drawer
    v-model="visible"
    :title="title"
    size="94%"
    destroy-on-close
    class="codegen-drawer"
    @close="handleClose"
  >
    <template v-if="currentStep !== PREVIEW_STEP">
      <div class="step-tabs">
        <button
          v-for="item in STEPS"
          :key="item.step"
          type="button"
          class="step-tab"
          :class="{ active: currentStep === item.step, complete: currentStep > item.step }"
          @click="goToStep(item.step)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.step + 1 }}. {{ item.title }}</span>
        </button>
      </div>
      <div v-loading="loading" :element-loading-text="loadingText" class="drawer-content">
        <BasicConfigStep
          v-show="currentStep === 0"
          ref="basicConfigRef"
          v-model="genConfigFormData"
          :menu-options="menuOptions"
        />
        <FieldDefinitionStep
          v-show="currentStep === 1"
          v-model="genConfigFormData"
          :dict-options="dictOptions"
        />
        <FormConfigStep v-show="currentStep === 2" v-model="genConfigFormData" />
        <DeleteConfigStep v-show="currentStep === 3" v-model="genConfigFormData" />
        <QueryConfigStep v-show="currentStep === 4" v-model="genConfigFormData" />
        <ListConfigStep v-show="currentStep === 5" v-model="genConfigFormData" />
      </div>
    </template>
    <template v-else>
      <div class="preview-heading">
        <div>
          <strong>代码预览</strong>
          <span>已按当前配置生成 Web、App 与 FastAPI 代码</span>
        </div>
        <el-button @click="currentStep = 5">
          <el-icon><Edit /></el-icon>
          返回配置
        </el-button>
      </div>
      <div
        v-loading="loading"
        :element-loading-text="loadingText"
        class="drawer-content preview-content"
      >
        <PreviewStep
          ref="previewRef"
          :gen-config-form-data="genConfigFormData"
          :preview-scope="previewScope"
          :preview-types="previewTypes"
          :preview-type-options="previewTypeOptions"
          :filtered-tree-data="filteredTreeData"
          :code="code"
          :current-file-key="currentFileKey"
          :table-name="currentTableName"
          @update:preview-scope="previewScope = $event"
          @update:preview-types="previewTypes = $event"
          @file-click="handleFileTreeNodeClick"
          @copy="handleCopyCode"
        />
      </div>
    </template>

    <template #footer>
      <div class="drawer-footer">
        <el-button v-if="currentStep > 0 && currentStep !== PREVIEW_STEP" @click="currentStep--">
          <el-icon><Back /></el-icon>
          上一步
        </el-button>
        <span v-else />
        <div class="footer-actions">
          <el-button @click="handleClose">取消</el-button>
          <template v-if="currentStep !== PREVIEW_STEP">
            <el-button v-if="currentStep < 5" type="primary" @click="handleNext">
              下一步
              <el-icon><Right /></el-icon>
            </el-button>
            <el-button v-else type="primary" :loading="loading" @click="handleSaveAndPreview">
              <el-icon><View /></el-icon>
              保存并预览
            </el-button>
          </template>
          <template v-else>
            <el-button type="primary" :loading="loading" @click="handleDownload">
              <el-icon><Download /></el-icon>
              下载代码
            </el-button>
            <el-button type="primary" plain :disabled="!canWriteToLocal" @click="openWriteDialog()">
              <el-icon><FolderOpened /></el-icon>
              写入本地
            </el-button>
          </template>
        </div>
      </div>
    </template>

    <WriteLocalDialog
      v-model="writeDialogVisible"
      :can-write-to-local="canWriteToLocal"
      :supports-f-s-access="supportsFSAccess"
      :frontend-dir-path="frontendDirPath"
      :backend-dir-path="backendDirPath"
      :app-dir-path="appDirPath"
      :write-scope="writeScope"
      :overwrite-mode="overwriteMode"
      :write-progress="writeProgress"
      :write-running="writeRunning"
      @update:write-scope="writeScope = $event"
      @update:overwrite-mode="overwriteMode = $event"
      @pick-frontend-dir="pickFrontendDir"
      @pick-backend-dir="pickBackendDir"
      @pick-app-dir="pickAppDir"
      @confirm-write="confirmWrite"
    />
  </el-drawer>
</template>

<script setup lang="ts">
import GeneratorAPI from "@/api/codegen";
import { useGenConfig } from "../composables/useGenConfig";
import { useCodePreview } from "../composables/useCodePreview";
import { useLocalWrite } from "../composables/useLocalWrite";
import BasicConfigStep from "./BasicConfigStep.vue";
import DeleteConfigStep from "./DeleteConfigStep.vue";
import FieldDefinitionStep from "./FieldDefinitionStep.vue";
import FormConfigStep from "./FormConfigStep.vue";
import ListConfigStep from "./ListConfigStep.vue";
import PreviewStep from "./PreviewStep.vue";
import QueryConfigStep from "./QueryConfigStep.vue";
import WriteLocalDialog from "./WriteLocalDialog.vue";

const PREVIEW_STEP = 6;
const STEPS = [
  { step: 0, title: "基础命名", icon: "InfoFilled" },
  { step: 1, title: "字段列表", icon: "List" },
  { step: 2, title: "增加、修改", icon: "Edit" },
  { step: 3, title: "删除", icon: "Delete" },
  { step: 4, title: "查询条件", icon: "DocumentChecked" },
  { step: 5, title: "列表", icon: "Grid" },
] as const;

const visible = defineModel<boolean>("visible", { required: true });
defineProps<{ title: string }>();
const emit = defineEmits<{ success: [] }>();
const currentStep = ref(0);
const currentTableName = ref("");
const loading = ref(false);
const loadingText = ref("加载中...");
const basicConfigRef = ref();
const previewRef = ref();

const { genConfigFormData, menuOptions, dictOptions, loadConfig, saveConfig, validateBasic } =
  useGenConfig();
const {
  filteredTreeData,
  previewScope,
  previewTypes,
  previewTypeOptions,
  code,
  currentFileKey,
  handlePreview,
  handleFileTreeNodeClick,
  handleCopyCode,
} = useCodePreview(genConfigFormData);
const {
  supportsFSAccess,
  writeDialog,
  frontendDirPath,
  backendDirPath,
  appDirPath,
  writeScope,
  overwriteMode,
  writeProgress,
  writeRunning,
  canWriteToLocal,
  openWriteDialog,
  setPreviewFiles,
  pickFrontendDir,
  pickBackendDir,
  pickAppDir,
  confirmWrite,
} = useLocalWrite(genConfigFormData);
const writeDialogVisible = computed({
  get: () => writeDialog.visible,
  set: (value) => (writeDialog.visible = value),
});

watch(currentStep, (value) => {
  if (value === PREVIEW_STEP) nextTick(() => previewRef.value?.refreshEditor());
});

async function open(tableName: string, mode: "config" | "preview" = "config") {
  currentTableName.value = tableName;
  currentStep.value = 0;
  loading.value = true;
  try {
    await loadConfig(tableName);
    if (mode === "preview") {
      await doPreview(tableName);
      currentStep.value = PREVIEW_STEP;
    }
  } catch {
    ElMessage.error("获取代码生成配置失败");
    visible.value = false;
  } finally {
    loading.value = false;
  }
}

function goToStep(step: number) {
  if (step > 0 && !validateBasic()) return;
  currentStep.value = step;
}
async function handleNext() {
  if (currentStep.value === 0) {
    const valid = await basicConfigRef.value?.validate();
    if (!valid || !validateBasic()) return;
  }
  if (currentStep.value < 5) currentStep.value++;
}

function validateFields() {
  const fields = genConfigFormData.value.fieldConfigs || [];
  const names = fields.map((item) => item.fieldName?.trim() || "");
  if (names.some((name) => !/^[A-Za-z_][A-Za-z0-9_]*$/.test(name))) {
    ElMessage.error("字段命名必须是有效的 Python / TypeScript 标识符");
    currentStep.value = 1;
    return false;
  }
  if (new Set(names).size !== names.length) {
    ElMessage.error("字段命名不能重复");
    currentStep.value = 1;
    return false;
  }
  if (fields.some((item) => !item.fieldComment?.trim())) {
    ElMessage.error("请补全所有字段描述");
    currentStep.value = 1;
    return false;
  }
  if (fields.some((item) => !item.frontendType?.trim())) {
    ElMessage.error("请为每个字段选择前端类型");
    currentStep.value = 1;
    return false;
  }
  return true;
}

async function handleSaveAndPreview() {
  if (!validateBasic() || !validateFields()) return;
  loading.value = true;
  loadingText.value = "正在保存配置并生成预览...";
  try {
    await saveConfig(currentTableName.value);
    await doPreview(currentTableName.value);
    currentStep.value = PREVIEW_STEP;
    emit("success");
    ElMessage.success("配置已保存");
  } catch {
    ElMessage.error("保存或生成失败，请检查配置");
  } finally {
    loading.value = false;
    loadingText.value = "加载中...";
  }
}

async function doPreview(tableName: string) {
  const files = await handlePreview(tableName);
  setPreviewFiles(files);
}
async function handleDownload() {
  loading.value = true;
  loadingText.value = "正在打包代码...";
  try {
    await GeneratorAPI.download(
      currentTableName.value,
      genConfigFormData.value.pageType || "classic"
    );
    ElMessage.success("代码下载成功");
  } catch {
    ElMessage.error("代码下载失败，请稍后重试");
  } finally {
    loading.value = false;
  }
}
function handleClose() {
  visible.value = false;
}
defineExpose({ open });
</script>

<style scoped lang="scss">
.codegen-drawer {
  :deep(.el-drawer__header) {
    padding: 16px 22px;
    margin-bottom: 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }
  :deep(.el-drawer__body) {
    display: flex;
    flex-direction: column;
    padding: 0;
    overflow: hidden;
    background: var(--el-fill-color-extra-light);
  }
  :deep(.el-drawer__footer) {
    padding: 12px 22px;
    border-top: 1px solid var(--el-border-color-lighter);
  }
}
.step-tabs {
  display: flex;
  flex: 0 0 auto;
  gap: 4px;
  padding: 16px 22px 0;
  overflow-x: auto;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.step-tab {
  display: inline-flex;
  gap: 7px;
  align-items: center;
  padding: 11px 16px 13px;
  color: var(--el-text-color-primary);
  white-space: nowrap;
  cursor: pointer;
  background: transparent;
  border: 0;
  border-bottom: 3px solid transparent;
}
.step-tab:hover,
.step-tab.complete {
  color: var(--el-color-primary);
}
.step-tab.active {
  font-weight: 600;
  color: var(--el-color-primary);
  border-bottom-color: var(--el-color-primary);
}
.drawer-content {
  flex: 1;
  min-height: 0;
  padding: 18px 22px;
  overflow: auto;
}
.preview-content {
  padding-top: 12px;
}
.preview-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 22px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.preview-heading > div {
  display: grid;
  gap: 3px;
}
.preview-heading span {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.drawer-footer,
.footer-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
}
@media (max-width: 768px) {
  .drawer-content {
    padding: 12px;
  }
  .step-tabs {
    padding-right: 8px;
    padding-left: 8px;
  }
  .step-tab {
    padding-right: 11px;
    padding-left: 11px;
  }
  .drawer-footer {
    align-items: flex-end;
  }
  .footer-actions {
    flex-wrap: wrap;
    justify-content: flex-end;
  }
}
</style>
