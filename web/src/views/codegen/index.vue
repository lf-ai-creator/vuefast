<template>
  <div class="page-container">
    <TableList
      ref="tableListRef"
      @configure="(tableName) => handleOpenDrawer(tableName, 'config')"
      @preview="(tableName) => handleOpenDrawer(tableName, 'preview')"
      @reset-config="handleResetConfig"
    />

    <GeneratorDrawer
      ref="drawerRef"
      v-model:visible="drawerVisible"
      :title="drawerTitle"
      @success="tableListRef?.handleQuery()"
    />
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "Codegen" });

import TableList from "./components/TableList.vue";
import GeneratorDrawer from "./components/GeneratorDrawer.vue";

const drawerVisible = ref(false);
const drawerTitle = ref("");
const drawerRef = ref();
const tableListRef = ref();

function handleOpenDrawer(tableName: string, mode: "config" | "preview") {
  drawerTitle.value = `${tableName} · ${mode === "config" ? "代码配置" : "代码预览"}`;
  drawerVisible.value = true;
  nextTick(() => {
    drawerRef.value?.open(tableName, mode);
  });
}

function handleResetConfig(tableName: string) {
  tableListRef.value?.handleResetConfig(tableName);
}
</script>
