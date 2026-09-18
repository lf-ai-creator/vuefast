import { checkLogin } from "@/utils/auth";

/**
 * 扫码登录 PC 端
 *
 * 调起相机扫描 PC 端登录二维码，校验票据后跳转扫码确认页。
 * 未登录时跳转登录页，用户取消扫码静默处理。
 */
export function useScanLogin() {
  const toast = useToast();
  const scanLogin = async () => {
    if (!checkLogin()) return;
    try {
      const res = await uni.scanCode({ scanType: ["qrCode"] });
      const ticket = (res.result || "").trim();
      if (!ticket) {
        toast.info("无效的二维码");
        return;
      }
      uni.navigateTo({
        url: `/subPages/mine/scan-confirm/index?ticket=${encodeURIComponent(ticket)}`,
      });
    } catch {
      // 用户取消扫码，静默处理
    }
  };

  return { scanLogin };
}
