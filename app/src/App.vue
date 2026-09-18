<script setup lang="ts">
import { onLaunch } from "@dcloudio/uni-app";
import { useThemeStore } from "@/store";

onLaunch(() => {
  const themeStore = useThemeStore();
  themeStore.initTheme();
});
</script>

<style lang="scss">
@use "@wot-ui/ui/styles/theme/index.scss" as *;
</style>
