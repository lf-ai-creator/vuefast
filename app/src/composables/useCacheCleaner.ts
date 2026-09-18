import { ref } from "vue";
import { useToast } from "@wot-ui/ui";
import { Storage } from "@/utils/storage";
import { formatBytes } from "@/utils/format";

/**
 * 缓存体积与清理
 *
 * 只统计并清理可重建的缓存（如用户信息缓存），登录态与主题偏好不参与，
 * 避免像 uni.clearStorage() 那样把 token 一起清掉导致下次启动退出登录。
 */
export function useCacheCleaner() {
  const toast = useToast();
  const usageText = ref("计算中...");
  const isClearing = ref(false);

  async function loadUsage() {
    try {
      usageText.value = formatBytes(Storage.getClearableBytes());
    } catch {
      usageText.value = "获取失败";
    }
  }

  async function clear() {
    if (usageText.value === "获取失败") {
      toast.info("获取缓存信息失败，请稍后重试");
      return;
    }
    if (isClearing.value) {
      return;
    }
    if (usageText.value === "0B") {
      toast.info("暂无缓存需要清理");
      return;
    }

    try {
      isClearing.value = true;
      const removed = Storage.clearCache();
      await loadUsage();
      if (removed > 0) {
        toast.success("清理成功");
      } else {
        toast.info("暂无缓存需要清理");
      }
    } catch {
      toast.error("清理失败");
    } finally {
      isClearing.value = false;
    }
  }

  return { usageText, isClearing, loadUsage, clear };
}
