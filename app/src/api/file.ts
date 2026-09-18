import { getAccessToken } from "@/utils/auth";
import { RequestError } from "@/utils/request";
import { ApiCode } from "@/enums/api-code-enum";

// H5 使用 VITE_APP_BASE_API 作为代理路径，其他平台使用 VITE_APP_API_URL 作为请求路径
let baseApi = import.meta.env.VITE_APP_API_URL;
// #ifdef H5
baseApi = import.meta.env.VITE_APP_BASE_API;
// #endif

const FileAPI = {
  /**
   * 文件上传地址
   */
  uploadUrl: baseApi + "/api/v1/files",

  /**
   * 上传文件（uni.uploadFile 专用通道，鉴权与错误语义与统一请求层保持一致）
   *
   * @param filePath 本地文件路径
   */
  upload(filePath: string): Promise<FileInfo> {
    return new Promise((resolve, reject) => {
      uni.uploadFile({
        url: this.uploadUrl,
        filePath: filePath,
        name: "file",
        header: {
          Authorization: getAccessToken() ? `Bearer ${getAccessToken()}` : "",
        },
        formData: {},
        success: (response) => {
          let resData: ApiResponse<FileInfo>;
          try {
            resData = JSON.parse(response.data) as ApiResponse<FileInfo>;
          } catch {
            reject(new RequestError("文件上传响应解析失败", response.statusCode));
            return;
          }
          if (resData.code === ApiCode.SUCCESS) {
            resolve(resData.data);
          } else {
            reject(
              new RequestError(resData.msg || "文件上传失败", response.statusCode, resData.code)
            );
          }
        },
        fail: (error) => {
          reject(new RequestError(error.errMsg || "文件上传请求失败", 0));
        },
      });
    });
  },
};

export default FileAPI;

/**
 * 文件API类型声明
 */
export interface FileInfo {
  /** 文件名 */
  name: string;
  /** 文件路径 */
  url: string;
}
