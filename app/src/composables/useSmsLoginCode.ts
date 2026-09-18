import { ref } from "vue";
import { useToast } from "@wot-ui/ui";
import { useCountdown } from "@/composables/useCountdown";
import { getErrorMessage } from "@/utils/error";
import AuthAPI from "@/api/auth";

/** 手机号格式校验 */
export function isValidMobile(mobile: string): boolean {
  return /^1\d{10}$/.test((mobile || "").trim());
}

/**
 * 登录短信验证码发送（含 60s 倒计时与发送锁）
 *
 * @returns countdown 剩余秒数、isSending 发送中标志、sendCode 发送函数、resetCountdown 重置倒计时
 */
export function useSmsLoginCode() {
  const toast = useToast();
  const { countdown, start, stop } = useCountdown(60);
  /** 发送中标志：请求返回前阻止重复点击（倒计时在发送成功后才启动） */
  const isSending = ref(false);

  /** 发送验证码，失败提示由这里统一处理 */
  async function sendCode(mobile: string, fallback = "发送失败"): Promise<boolean> {
    if (isSending.value || countdown.value > 0) return false;
    if (!isValidMobile(mobile)) {
      toast.error("请输入正确的手机号");
      return false;
    }
    isSending.value = true;
    try {
      await AuthAPI.sendSmsLoginCode(mobile.trim());
      toast.success("验证码已发送");
      start();
      return true;
    } catch (error) {
      toast.error(getErrorMessage(error, fallback));
      return false;
    } finally {
      isSending.value = false;
    }
  }

  function resetCountdown() {
    stop();
  }

  return { countdown, isSending, sendCode, resetCountdown };
}
