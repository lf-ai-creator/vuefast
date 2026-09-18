import request from "@/utils/request";

const AUTH_BASE_URL = "/api/v1/auth";
const WXMA_AUTH_BASE_URL = "/api/v1/wxma/auth";

export interface PasswordLoginParams {
  username: string;
  password: string;
  captchaId?: string;
  captchaCode?: string;
}

export interface LoginResult {
  accessToken: string;
  refreshToken?: string;
  tokenType: string;
  expiresIn: number;
  isNewUser?: boolean;
  needBindMobile?: boolean;
  openid?: string;
}

export interface Captcha {
  captchaId: string;
  captchaBase64: string;
}

export interface SmsLoginParams {
  mobile: string;
  code: string;
}

export interface WxMaLoginResult {
  accessToken?: string;
  refreshToken?: string;
  tokenType?: string;
  expiresIn?: number;
  isNewUser: boolean;
  needBindMobile: boolean;
  openid?: string;
}

export interface WxMaPhoneLoginParams {
  loginCode: string;
  phoneCode: string;
}

export interface WxMaBindMobileParams {
  openid: string;
  mobile: string;
  smsCode: string;
}

/** APP 端扫码相关接口（scan/confirm/cancel）的响应 */
export interface QrCodeScanResult {
  /** 当前票据状态，APP 端扫码后流转为 SCANNED → CONFIRMED / CANCELED */
  status: "SCANNED" | "CONFIRMED" | "CANCELED";
  /** 脱敏昵称，scan 成功后返回，用于确认页展示请求登录的用户 */
  nickname?: string;
  /** 头像 URL，scan 成功后返回 */
  avatar?: string;
}

const AuthAPI = {
  /** 获取图形验证码 */
  getCaptcha(): Promise<Captcha> {
    return request<Captcha>({
      url: `${AUTH_BASE_URL}/captcha`,
      method: "GET",
    });
  },

  /** 账号密码登录 */
  loginByPassword(data: PasswordLoginParams): Promise<LoginResult> {
    return request<LoginResult>({
      url: `${AUTH_BASE_URL}/login`,
      method: "POST",
      data: data,
    });
  },

  /**
   * 发送短信验证码
   *
   * 短信服务接入前此接口返回不可用，请使用账号密码登录
   */
  sendSmsLoginCode(mobile: string): Promise<void> {
    const mobileSafe = encodeURIComponent(mobile);
    return request({
      url: `${AUTH_BASE_URL}/sms/code?mobile=${mobileSafe}`,
      method: "POST",
    });
  },

  /** 短信验证码登录 */
  loginBySms(data: SmsLoginParams): Promise<LoginResult> {
    const mobileSafe = encodeURIComponent(data.mobile);
    const codeSafe = encodeURIComponent(data.code);
    return request<LoginResult>({
      url: `${AUTH_BASE_URL}/login/sms?mobile=${mobileSafe}&code=${codeSafe}`,
      method: "POST",
    });
  },

  /**
   * 微信小程序静默登录
   *
   * 适用场景：个人小程序
   * - 已绑定手机号的用户：直接返回 token，登录成功
   * - 未绑定手机号的用户：返回 openid，需调用绑定手机号接口
   */
  wxMaSilentLogin(code: string): Promise<WxMaLoginResult> {
    return request<WxMaLoginResult>({
      url: `${WXMA_AUTH_BASE_URL}/silent-login?code=${encodeURIComponent(code)}`,
      method: "POST",
    });
  },

  /**
   * 微信小程序手机号快捷登录
   *
   * 适用场景：企业认证小程序（已开通手机号快捷登录权限）
   * 一步完成登录，无需绑定流程，自动创建新用户
   */
  wxMaPhoneLogin(data: WxMaPhoneLoginParams): Promise<LoginResult> {
    return request<LoginResult>({
      url: `${WXMA_AUTH_BASE_URL}/phone-login`,
      method: "POST",
      data: data,
    });
  },

  /**
   * 微信小程序绑定手机号
   *
   * 短信服务接入前此接口返回不可用，请使用账号密码登录
   */
  wxMaBindMobile(data: WxMaBindMobileParams): Promise<LoginResult> {
    return request<LoginResult>({
      url: `${WXMA_AUTH_BASE_URL}/bind-mobile`,
      method: "POST",
      data: data,
    });
  },

  /** 登出 */
  logout() {
    return request({
      url: `${AUTH_BASE_URL}/logout`,
      method: "DELETE",
    });
  },

  // ============ 扫码登录 ============

  /**
   * 标记已扫码
   *
   * 把当前 APP 登录用户与票据绑定，PC 端 status 随即进入 SCANNED 并展示头像昵称
   */
  markQrLoginScanned(ticket: string): Promise<QrCodeScanResult> {
    return request<QrCodeScanResult>({
      url: `${AUTH_BASE_URL}/qr-code/scan`,
      method: "POST",
      data: { ticket },
    });
  },

  /**
   * 确认扫码登录
   *
   * 真正的授权动作，授权后 PC 端 status 进入 CONFIRMED，可换取会话令牌
   */
  confirmQrLogin(ticket: string): Promise<QrCodeScanResult> {
    return request<QrCodeScanResult>({
      url: `${AUTH_BASE_URL}/qr-code/confirm`,
      method: "POST",
      data: { ticket },
    });
  },

  /**
   * 取消扫码登录
   *
   * 撤回本次扫码，PC 端 status 进入 CANCELED
   */
  cancelQrLogin(ticket: string): Promise<QrCodeScanResult> {
    return request<QrCodeScanResult>({
      url: `${AUTH_BASE_URL}/qr-code/cancel`,
      method: "POST",
      data: { ticket },
    });
  },
};

export default AuthAPI;
