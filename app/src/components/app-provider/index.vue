<script lang="ts" setup>
import { storeToRefs } from "pinia";
import { useThemeStore } from "@/store";

/**
 * 全局应用容器（主题配置唯一来源）
 *
 * 页面内容与全局弹层（notify/toast/dialog）统一从 wd-config-provider 继承主题，
 * default / tabbar 两个 layout 共用，保证配置同源。
 */
const themeStore = useThemeStore();
const { themeMode, themeVars } = storeToRefs(themeStore);

// 页面自定义样式用的主题色（含透明度变体）与深色模式下的卡片填充色
const HEX6_RE = /^#[0-9a-fA-F]{6}$/;

const providerStyle = computed(() => {
  const primary = themeStore.selectedThemeColor.primary;
  const styles = [`--color-primary: ${primary}`, "--wot-filled-oppo: var(--color-bg-card)"];
  if (HEX6_RE.test(primary)) {
    const bigint = Number.parseInt(primary.slice(1), 16);
    const rgb = `${(bigint >> 16) & 255}, ${(bigint >> 8) & 255}, ${bigint & 255}`;
    styles.push(
      `--color-primary-alpha-20: rgba(${rgb}, 0.2)`,
      `--color-primary-alpha-15: rgba(${rgb}, 0.15)`
    );
  }
  return styles.join("; ");
});
</script>

<script lang="ts">
export default {
  name: "AppProvider",
  options: {
    virtualHost: true,
    styleIsolation: "shared",
  },
};
</script>

<template>
  <wd-config-provider
    :theme="themeMode"
    :theme-vars="themeVars"
    :custom-style="providerStyle"
    :button="{ type: 'primary' }"
    :tag="{ variant: 'plain' }"
  >
    <slot />
    <wd-notify />
    <wd-toast />
    <wd-dialog />
  </wd-config-provider>
</template>
