<template>
  <div>
    <div
      class="command-palette-trigger"
      role="button"
      tabindex="0"
      aria-label="打开搜索面板"
      @click="open"
      @keydown.enter.prevent="open"
      @keydown.space.prevent="open"
    >
      <div class="command-palette-trigger__left">
        <div class="i-svg:search" />
        <span class="command-palette-trigger__text">搜索菜单</span>
      </div>
      <kbd class="command-palette-trigger__kbd">Ctrl K</kbd>
    </div>

    <el-dialog
      v-model="visible"
      class="command-palette-dialog-shell"
      width="min(720px, calc(100vw - 32px))"
      :close-on-click-modal="true"
      :show-close="false"
      @close="close"
    >
      <div class="command-palette-dialog">
        <el-input
          ref="inputRef"
          v-model="keyword"
          class="command-palette-input"
          placeholder="搜索菜单"
          @input="onSearch"
          @keydown="handleInputKeydown"
        >
          <template #prefix>
            <div class="i-svg:search" />
          </template>
          <template #suffix>
            <div class="command-palette-input__suffix">
              <div
                class="i-svg:close"
                role="button"
                tabindex="0"
                aria-label="关闭"
                @click="close"
              />
            </div>
          </template>
        </el-input>

        <div class="command-palette-results">
          <div v-if="displayList.length === 0" class="command-palette-empty">
            <div class="command-palette-empty__icon"><div class="i-svg:search" /></div>
            <span>没有匹配的菜单</span>
          </div>

          <ul v-else class="command-palette-list">
            <li class="command-palette-list__label">
              {{ results.length ? "搜索结果" : "最近访问" }}
              <span>{{ displayList.length }} 项</span>
            </li>
            <li
              v-for="(item, idx) in displayList"
              :key="item.path + idx"
              :class="['command-palette-item', { 'is-active': activeIndex === idx }]"
              :aria-current="activeIndex === idx ? 'true' : undefined"
              @mouseenter="activeIndex = idx"
              @click="onGo(item)"
            >
              <div class="command-palette-item__main">
                <div class="command-palette-item__icon"><div class="i-svg:menu" /></div>
                <div class="command-palette-item__content">
                  <div class="command-palette-item__title">{{ item.title }}</div>
                  <div class="command-palette-item__path">{{ item.path }}</div>
                </div>
              </div>
              <div class="command-palette-item__arrow" aria-hidden="true">›</div>
            </li>
          </ul>
        </div>

        <div class="command-palette-hints">
          <div class="command-palette-hint">
            <div class="command-palette-hint__key"><div class="i-svg:up" /></div>
            <div class="command-palette-hint__key"><div class="i-svg:down" /></div>
            <span class="command-palette-hint__text">切换</span>
          </div>
          <div class="command-palette-hint">
            <div class="command-palette-hint__key"><div class="i-svg:enter" /></div>
            <span class="command-palette-hint__text">选择</span>
          </div>
          <div class="command-palette-hint">
            <div class="command-palette-hint__key"><div class="i-svg:esc" /></div>
            <span class="command-palette-hint__text">关闭</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useCommandPalette } from "./useCommandPalette";

const {
  visible,
  keyword,
  results,
  history,
  activeIndex,
  inputRef,
  open,
  close,
  onSearch,
  onSelect,
  onNavigate,
  onGo,
} = useCommandPalette();

const displayList = computed(() => (results.value.length ? results.value : history.value));

const handleInputKeydown: (evt: KeyboardEvent | Event) => void = (evt) => {
  if (!(evt instanceof KeyboardEvent)) return;
  const e = evt;
  const key = e.key.toLowerCase();

  if (key === "escape") {
    e.preventDefault();
    close();
    return;
  }

  if (key === "arrowup") {
    e.preventDefault();
    onNavigate("up");
    return;
  }

  if (key === "arrowdown") {
    e.preventDefault();
    onNavigate("down");
    return;
  }

  if (key === "enter") {
    e.preventDefault();
    if (displayList.value.length === 0) return;
    if (activeIndex.value < 0) activeIndex.value = 0;
    onSelect();
  }
};
</script>

<style scoped>
.command-palette-trigger {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: space-between;
  width: 184px;
  height: 28px;
  padding: 0 8px 0 10px;
  user-select: none;
  background: color-mix(in srgb, var(--el-fill-color-extra-light) 82%, transparent);
  border: 1px solid color-mix(in srgb, var(--el-border-color-light) 78%, transparent);
  border-radius: 7px;
  transition:
    background-color 0.16s,
    border-color 0.16s;
}

.command-palette-trigger__left {
  display: flex;
  gap: 6px;
  align-items: center;
  min-width: 0;
}

.command-palette-trigger__left :deep([class^="i-svg:"]) {
  flex-shrink: 0;
  width: 14px;
  height: 14px;
  color: var(--el-text-color-secondary) !important;
}

.command-palette-trigger__text {
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
}

.command-palette-trigger__kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 18px;
  padding: 0 6px;
  font-size: 11px;
  line-height: 1;
  color: var(--el-text-color-placeholder);
  white-space: nowrap;
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
}

.command-palette-trigger:focus-visible {
  outline: 2px solid var(--el-color-primary);
  outline-offset: 2px;
}

.command-palette-trigger:hover {
  background: var(--el-fill-color-light);
  border-color: var(--el-border-color);
}

.command-palette-trigger:active {
  transform: translateY(1px);
}

:global(.command-palette-dialog-shell .el-dialog__header) {
  display: none;
}

:global(.command-palette-dialog-shell .el-dialog__body) {
  padding: 16px;
}

.command-palette-dialog {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.command-palette-input :deep(.el-input__wrapper) {
  min-height: 42px;
  padding: 0 12px;
  border-radius: 9px;
  box-shadow:
    0 0 0 1px var(--el-color-primary-light-7) inset,
    0 4px 14px rgb(22 93 255 / 8%);
}

.command-palette-input :deep(.el-input__inner) {
  font-size: 14px;
}

.command-palette-input__suffix {
  display: inline-flex;
  gap: 10px;
  align-items: center;
}

.command-palette-input__suffix :deep([class^="i-svg:"]) {
  font-size: 16px;
  color: var(--el-text-color-secondary);
}

.command-palette-input__suffix :deep([class^="i-svg:"]):hover {
  color: var(--el-color-primary);
}

.command-palette-results {
  min-height: 72px;
  max-height: min(48vh, 420px);
  padding: 2px;
  overflow: auto;
  scrollbar-width: thin;
}

.command-palette-empty {
  display: grid;
  place-items: center;
  min-height: 72px;
  padding: 16px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  text-align: center;
}

.command-palette-empty__icon {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  margin-bottom: 6px;
  color: var(--el-text-color-placeholder);
  background: var(--el-fill-color-light);
  border-radius: 50%;
}

.command-palette-empty__icon :deep([class^="i-svg:"]) {
  font-size: 14px;
}

.command-palette-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0;
  margin: 0;
  list-style: none;
}

.command-palette-list__label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--el-text-color-placeholder);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.command-palette-list__label span {
  font-weight: 400;
  letter-spacing: 0;
}

.command-palette-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 52px;
  padding: 10px 12px;
  cursor: pointer;
  border: 1px solid transparent;
  border-radius: 8px;
  transition:
    background-color 0.14s,
    border-color 0.14s;
}

.command-palette-item__main {
  display: flex;
  flex: 1;
  gap: 10px;
  align-items: center;
  min-width: 0;
}

.command-palette-item__icon {
  display: grid;
  flex: 0 0 28px;
  place-items: center;
  width: 28px;
  height: 28px;
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 7px;
}

.command-palette-item__icon :deep([class^="i-svg:"]) {
  font-size: 14px;
}

.command-palette-item__content {
  min-width: 0;
}

.command-palette-item:hover {
  background: var(--el-fill-color-light);
}

.command-palette-item.is-active {
  background: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-8);
}

.command-palette-item__title {
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  white-space: nowrap;
}

.command-palette-item__path {
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
}

.command-palette-item__arrow {
  display: grid;
  flex: 0 0 24px;
  place-items: center;
  width: 24px;
  height: 24px;
  margin-left: 8px;
  color: var(--el-text-color-placeholder);
  opacity: 0;
  transition:
    color 0.14s,
    opacity 0.14s,
    transform 0.14s;
}

.command-palette-item:hover .command-palette-item__arrow,
.command-palette-item.is-active .command-palette-item__arrow {
  color: var(--el-color-primary);
  opacity: 1;
  transform: translateX(2px);
}

.command-palette-hints {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  align-items: center;
  padding: 10px 2px 0;
  border-top: 1px solid var(--el-border-color-lighter);
}

.command-palette-hint {
  display: inline-flex;
  gap: 6px;
  align-items: center;
}

.command-palette-hint__key {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 22px;
  padding: 0 6px;
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
}

.command-palette-hint__key :deep([class^="i-svg:"]) {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.command-palette-hint__text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

@media (max-width: 768px) {
  .command-palette-trigger {
    justify-content: center;
    width: 32px;
    padding: 0;
    background: transparent;
    border-color: transparent;
  }

  .command-palette-trigger__text,
  .command-palette-trigger__kbd {
    display: none;
  }

  :global(.command-palette-dialog-shell .el-dialog__body) {
    padding: 12px;
  }

  .command-palette-hints {
    gap: 8px 12px;
  }
}
</style>
