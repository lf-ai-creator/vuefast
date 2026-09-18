<template>
  <web-view :src="url" />
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";

definePage({
  name: "webview",
  style: { navigationBarTitleText: "网页" },
  layout: "blank",
});

const url = ref("");

onLoad((query) => {
  if (query?.url) {
    url.value = decodeURIComponent(query.url);
  }
});
</script>
