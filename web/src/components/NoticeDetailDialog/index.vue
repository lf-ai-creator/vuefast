<template>
  <el-dialog
    :model-value="modelValue"
    class="notice-detail-dialog"
    width="760px"
    append-to-body
    destroy-on-close
    align-center
    @update:model-value="emit('update:modelValue', $event)"
  >
    <template #header>
      <div class="notice-detail-dialog__header">
        <div class="notice-detail-dialog__header-icon">
          <el-icon><Bell /></el-icon>
        </div>
        <div class="notice-detail-dialog__header-title">通知公告详情</div>
      </div>
    </template>

    <article v-if="detail" class="notice-detail">
      <header class="notice-detail__summary">
        <h2 class="notice-detail__title">{{ detail.title || "未命名公告" }}</h2>

        <div class="notice-detail__information">
          <div class="notice-detail__meta">
            <span class="notice-detail__meta-item">
              <el-icon><User /></el-icon>
              {{ detail.publisherName || "系统管理员" }}
            </span>
            <span class="notice-detail__meta-divider" />
            <span class="notice-detail__meta-item">
              <el-icon><Clock /></el-icon>
              {{ formatTime(detail.publishTime) }}
            </span>
          </div>

          <div class="notice-detail__tags">
            <DictTag v-if="detail.type !== undefined" v-model="detail.type" code="notice_type" />
            <DictTag
              v-if="detail.level !== undefined && detail.level !== ''"
              v-model="detail.level"
              code="notice_level"
            />
            <el-tag v-if="detail.publishStatus === 0" type="info" effect="light">未发布</el-tag>
            <el-tag v-else-if="detail.publishStatus === 1" type="success" effect="light">
              已发布
            </el-tag>
            <el-tag v-else-if="detail.publishStatus === -1" type="warning" effect="light">
              已撤回
            </el-tag>
          </div>
        </div>
      </header>

      <div class="notice-detail__body">
        <div v-if="detail.content" class="notice-detail__content" v-html="detail.content" />
        <el-empty v-else :image-size="72" description="暂无公告内容" />
      </div>
    </article>

    <template #footer>
      <el-button type="primary" @click="emit('update:modelValue', false)">我知道了</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { Bell, Clock, User } from "@element-plus/icons-vue";
import type { NoticeDetail } from "@/api/system/notice";

defineOptions({ name: "NoticeDetailDialog" });

defineProps<{
  modelValue: boolean;
  detail: NoticeDetail | null;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
}>();

function formatTime(value?: string | Date | null): string {
  if (!value) return "暂无发布时间";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  const pad = (part: number) => String(part).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}
</script>

<style lang="scss">
.notice-detail-dialog {
  max-width: calc(100vw - 32px);
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 14px;
  box-shadow:
    0 20px 50px rgb(0 0 0 / 12%),
    0 4px 14px rgb(0 0 0 / 6%);

  .el-dialog__header {
    padding: 13px 18px;
    margin-right: 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  .el-dialog__headerbtn {
    top: 7px;
    right: 10px;
    width: 38px;
    height: 38px;
  }

  .el-dialog__body {
    padding: 0;
  }

  .el-dialog__footer {
    padding: 10px 18px;
    background: var(--el-fill-color-extra-light);
    border-top: 1px solid var(--el-border-color-lighter);
  }

  &__header {
    display: flex;
    gap: 9px;
    align-items: center;
  }

  &__header-icon {
    display: grid;
    place-items: center;
    width: 32px;
    height: 32px;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
    border: 1px solid var(--el-color-primary-light-8);
    border-radius: 8px;
  }

  &__header-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    letter-spacing: 0.2px;
  }
}

.notice-detail {
  &__summary {
    padding: 22px 28px 18px;
    background: linear-gradient(135deg, var(--el-color-primary-light-9), transparent 55%);
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  &__title {
    margin: 0;
    font-size: 20px;
    font-weight: 650;
    line-height: 1.45;
    color: var(--el-text-color-primary);
    overflow-wrap: anywhere;
  }

  &__information {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 16px;
    align-items: center;
    justify-content: space-between;
    margin-top: 13px;
  }

  &__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  &__meta-item {
    display: inline-flex;
    gap: 6px;
    align-items: center;
  }

  &__meta-divider {
    width: 1px;
    height: 12px;
    background: var(--el-border-color);
  }

  &__tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-items: center;

    .el-tag {
      height: 23px;
      padding: 0 8px;
      font-size: 12px;
      border-radius: 5px;
    }
  }

  &__body {
    min-height: 160px;
    max-height: min(50vh, 500px);
    padding: 22px 28px 26px;
    overflow-y: auto;
    overscroll-behavior: contain;
  }

  &__content {
    font-size: 15px;
    line-height: 1.8;
    color: var(--el-text-color-regular);
    overflow-wrap: anywhere;

    > :first-child {
      margin-top: 0;
    }

    > :last-child {
      margin-bottom: 0;
    }

    img,
    video,
    table {
      max-width: 100%;
    }

    img {
      height: auto;
      border-radius: 6px;
    }

    table {
      border-collapse: collapse;
    }

    th,
    td {
      padding: 8px 12px;
      border: 1px solid var(--el-border-color);
    }

    blockquote {
      padding: 10px 16px;
      margin-right: 0;
      margin-left: 0;
      color: var(--el-text-color-secondary);
      background: var(--el-fill-color-light);
      border-left: 3px solid var(--el-color-primary-light-5);
    }
  }
}

@media (max-width: 600px) {
  .notice-detail {
    &__summary,
    &__body {
      padding-right: 20px;
      padding-left: 20px;
    }

    &__title {
      font-size: 18px;
    }

    &__information {
      flex-direction: column;
      align-items: flex-start;
    }
  }
}
</style>
