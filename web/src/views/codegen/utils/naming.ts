/**
 * 代码生成命名转换
 *
 * 生成产物的目录命名必须与后端 `to_snake` 保持一致：
 * 后端包使用下划线目录，Web 与 App 使用短横线目录。
 */

/**
 * PascalCase / camelCase / kebab-case → snake_case
 *
 * @param value 实体名或表名
 * @returns 小写下划线命名
 */
export function toSnake(value?: string): string {
  return (value ?? "")
    .replace(/([a-z0-9])([A-Z])/g, "$1_$2")
    .replace(/([A-Z]+)([A-Z][a-z])/g, "$1_$2")
    .replace(/[^A-Za-z0-9]+/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_|_$/g, "")
    .toLowerCase();
}

/**
 * 任意命名 → kebab-case
 *
 * @param value 实体名或表名
 * @returns 小写短横线命名
 */
export function toKebab(value?: string): string {
  return toSnake(value).replace(/_/g, "-");
}
