<template>
  <div class="p-5">路由参数type：{{ type }}</div>
</template>

<script setup lang="ts">
defineOptions({
  name: "RouteParam",
  inheritAttrs: false,
});
import { useRoute } from "vue-router";

const route = useRoute();

// URL 参数优先；直接访问或目录重定向时使用菜单配置的默认参数。
const type = computed(() => route.query.type ?? route.meta.params?.type ?? "未提供");
</script>
