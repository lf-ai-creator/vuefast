import { ref, onUnmounted } from "vue";

/**
 * 倒计时（按截止时间计算剩余秒数，页面隐藏或切后台后恢复时仍保持准确）
 */
export function useCountdown(duration = 60) {
  const countdown = ref(0);
  const isRunning = ref(false);
  let timer: ReturnType<typeof setInterval> | null = null;
  let deadline = 0;

  function tick() {
    const remain = Math.ceil((deadline - Date.now()) / 1000);
    countdown.value = Math.max(0, remain);
    if (countdown.value <= 0) stop();
  }

  const start = () => {
    if (isRunning.value) return;

    deadline = Date.now() + duration * 1000;
    isRunning.value = true;
    tick();
    timer = setInterval(tick, 1000);
  };

  const stop = () => {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
    countdown.value = 0;
    isRunning.value = false;
  };

  onUnmounted(() => stop());

  return {
    countdown,
    isRunning,
    start,
    stop,
  };
}
