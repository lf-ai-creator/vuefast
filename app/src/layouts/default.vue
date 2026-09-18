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
  <!-- 默认布局：标准内容页容器（内边距/画布底色/满屏高由 .page 统一提供） -->
  <app-provider>
    <view class="page">
      <slot />
    </view>
  </app-provider>
</template>
