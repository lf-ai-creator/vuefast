<script lang="ts">
export default {
  options: {
    addGlobalClass: true,
    virtualHost: true,
    styleIsolation: "shared",
  },
};
</script>

<template>
  <!-- 全出血布局：不注入容器样式，页面自行管理背景/高度（在 definePage 声明 layout: "blank"） -->
  <app-provider>
    <slot />
  </app-provider>
</template>
