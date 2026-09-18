<template>
  <web-view :src="monitorUrl" />
</template>

<script setup lang="ts">
import { ref } from "vue";

definePage({
  name: "monitor",
  style: { navigationBarTitleText: "应用监控" },
  layout: "blank",
});
// SpringBoot Admin 监控地址
const monitorUrl = ref("http://localhost:9090/wallboard");
</script>
