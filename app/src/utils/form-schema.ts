import type { FormSchema } from "@wot-ui/ui/components/wd-form/types";

/** 单条校验规则（v1 FormRules 风格） */
export interface FormRule {
  /** 是否必填 */
  required?: boolean;
  /** 校验失败提示文案 */
  message?: string;
  /** 正则校验（仅对字符串值生效） */
  pattern?: RegExp;
  /** 字符串长度下限（含） */
  min?: number;
  /** 字符串长度上限（含） */
  max?: number;
  /**
   * 自定义校验：返回 true 表示通过；返回 false 按 message 提示；
   * 返回字符串则以该文案提示
   */
  validator?: (value: any, model: Record<string, any>) => boolean | string;
}

/**
 * v1 FormRules → v2 FormSchema 适配器
 * 将旧版 rules 格式转换为 v2 的 schema 格式
 */
export function toFormSchema(rules: Record<string, FormRule[]>): FormSchema {
  return {
    validate(model: Record<string, any>) {
      const issues: { path: Array<string | number>; message: string }[] = [];
      for (const [field, fieldRules] of Object.entries(rules)) {
        const value = model[field];
        for (const rule of fieldRules) {
          if (rule.required) {
            const isEmpty =
              value === undefined ||
              value === null ||
              (typeof value === "string" && value.trim() === "") ||
              (Array.isArray(value) && value.length === 0);
            if (isEmpty) {
              issues.push({ path: [field], message: rule.message || `${field} 为必填项` });
              break;
            }
          }
          if (typeof value === "string") {
            if (rule.min !== undefined && value.length < rule.min) {
              issues.push({
                path: [field],
                message: rule.message || `${field} 长度不能少于 ${rule.min} 个字符`,
              });
              break;
            }
            if (rule.max !== undefined && value.length > rule.max) {
              issues.push({
                path: [field],
                message: rule.message || `${field} 长度不能超过 ${rule.max} 个字符`,
              });
              break;
            }
            if (rule.pattern && !rule.pattern.test(value)) {
              issues.push({ path: [field], message: rule.message || `${field} 格式不正确` });
              break;
            }
          }
          if (rule.validator) {
            const result = rule.validator(value, model);
            if (result === false || typeof result === "string") {
              issues.push({
                path: [field],
                message:
                  typeof result === "string" ? result : rule.message || `${field} 校验不通过`,
              });
              break;
            }
          }
        }
      }
      return issues;
    },
  };
}
