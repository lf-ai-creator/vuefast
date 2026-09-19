export function formatBytes(size: number): string {
  if (size < 1024) {
    return size + "B";
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + "KB";
  } else {
    return (size / 1024 / 1024).toFixed(2) + "MB";
  }
}

/** 统一格式化日期时间到分钟级别，仅用于客户端展示。 */
export function formatDateTime(value: unknown): string {
  if (value === undefined || value === null || value === "") return "";
  if (value instanceof Date) {
    if (Number.isNaN(value.getTime())) return "";
    const pad = (part: number) => String(part).padStart(2, "0");
    return `${value.getFullYear()}-${pad(value.getMonth() + 1)}-${pad(value.getDate())} ${pad(value.getHours())}:${pad(value.getMinutes())}`;
  }
  const text = String(value).trim();
  const normalized = text.replace("T", " ").replace(/Z$/, "");
  const match = normalized.match(/^(\d{4}-\d{2}-\d{2})(?:\s+(\d{2}:\d{2}))?/);
  return match ? `${match[1]}${match[2] ? ` ${match[2]}` : ""}` : text;
}
