/**
 * API 响应码枚举
 *
 * 与后端 ResultCode 对齐（youlai-boot common/result/ResultCode.java），
 * 仅收录前端实际消费的响应码
 */
export const enum ApiCode {
  /** 成功 */
  SUCCESS = "00000",

  /** 访问令牌无效或已过期 */
  ACCESS_TOKEN_INVALID = "A0230",

  /** 刷新令牌无效或已过期 */
  REFRESH_TOKEN_INVALID = "A0231",
}
