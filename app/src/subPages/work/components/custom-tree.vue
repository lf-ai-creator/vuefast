<template>
  <view class="custom-tree">
    <view v-for="item in flatNodes" :key="item.value" class="custom-tree-node">
      <view
        class="custom-tree-node__content"
        :style="{ paddingLeft: item.level * 32 + 24 + 'rpx' }"
        @click="handleNodeClick(item)"
      >
        <!-- 展开/收起图标 -->
        <view class="custom-tree-node__expand" @click.stop="handleExpand(item)">
          <wd-icon
            v-if="item.hasChildren"
            :name="isExpanded(item.value) ? 'arrow-down' : 'arrow-right'"
            size="14"
            class="custom-tree-node__arrow"
            :class="{ 'custom-tree-node__arrow--expanded': isExpanded(item.value) }"
          />
          <view v-else class="custom-tree-node__expand-placeholder" />
        </view>

        <!-- 多选框 -->
        <view v-if="checkable" class="custom-tree-node__checkbox" @click.stop="handleCheck(item)">
          <wd-checkbox
            :model-value="isChecked(item.value)"
            :indeterminate="isIndeterminate(item.value)"
            :disabled="item.disabled"
            type="square"
          />
        </view>

        <!-- 内容插槽 -->
        <slot
          name="content"
          :node="item.raw"
          :level="item.level"
          :expanded="isExpanded(item.value)"
          :checked="isChecked(item.value)"
          :indeterminate="isIndeterminate(item.value)"
        >
          <view class="custom-tree-node__label-wrapper">
            <wd-icon
              v-if="item.hasChildren"
              name="folder"
              size="18"
              :color="
                isExpanded(item.value) ? 'var(--color-primary)' : 'var(--color-text-secondary)'
              "
            />
            <wd-icon v-else name="file" size="16" class="color-text-secondary" />
            <text class="custom-tree-node__label">{{ item.label }}</text>
          </view>
        </slot>

        <!-- 操作按钮 -->
        <slot name="action" :node="item.raw" :level="item.level">
          <view
            v-if="showAction"
            class="custom-tree-node__action"
            @click.stop="handleNodeAction(item)"
          >
            <wd-icon name="more" size="16" class="color-text-secondary" />
          </view>
        </slot>
      </view>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { ref, computed, watch } from "vue";

export interface TreeOption {
  [key: string]: unknown;
  value: string;
  label: string;
  children?: TreeOption[];
}

interface FlatNode extends TreeOption {
  level: number;
  hasChildren: boolean;
  raw: TreeOption;
}

interface Props {
  /** 树形数据源 */
  data?: TreeOption[];
  /** 节点值的字段名 */
  valueKey?: string;
  /** 节点标签的字段名 */
  labelKey?: string;
  /** 子节点的字段名 */
  childrenKey?: string;
  /** 默认展开的节点 key 数组 */
  defaultExpandedKeys?: string[];
  /** 是否默认展开所有节点 */
  defaultExpandAll?: boolean;
  /** 是否显示操作按钮区域 */
  showAction?: boolean;
  /** 是否开启多选 */
  checkable?: boolean;
  /** 选中的节点 key 数组（多选模式） */
  checkedKeys?: string[];
  /** 父子节点是否不联动（默认联动） */
  checkStrictly?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  valueKey: "value",
  labelKey: "label",
  childrenKey: "children",
  defaultExpandedKeys: () => [],
  defaultExpandAll: false,
  showAction: false,
  checkable: false,
  checkedKeys: () => [],
  checkStrictly: false,
});

const emit = defineEmits<{
  /** 点击节点时触发 */
  (_e: "click", _node: TreeOption): void;
  /** 展开/收起节点时触发 */
  (_e: "expand", _node: TreeOption, _expanded: boolean): void;
  /** 点击操作按钮时触发 */
  (_e: "action", _node: TreeOption): void;
  /** 多选选中变化时触发 */
  (_e: "check", _checkedKeys: string[], _info: { checked: boolean; node: TreeOption }): void;
}>();

/** 展开的节点 key 集合 */
const expandedKeys = ref<Set<string>>(new Set(props.defaultExpandedKeys));
/** 选中的节点 key 集合（多选模式，内部维护） */
const internalCheckedKeys = ref<Set<string>>(new Set(props.checkedKeys));

// 监听外部 checkedKeys 变化
watch(
  () => props.checkedKeys,
  (keys) => {
    internalCheckedKeys.value = new Set(keys);
  },
  { immediate: true }
);

/** 扁平化树结构，根据展开状态计算可见节点 */
const flatNodes = computed(() => {
  const result: FlatNode[] = [];
  function traverse(nodes: TreeOption[], level: number) {
    for (const node of nodes) {
      const children = node[props.childrenKey] as TreeOption[] | undefined;
      result.push({
        ...node,
        value: String(node[props.valueKey]),
        label: node[props.labelKey] as string,
        level,
        hasChildren: !!(children && children.length > 0),
        raw: node,
      });
      if (children && children.length > 0 && expandedKeys.value.has(String(node[props.valueKey]))) {
        traverse(children, level + 1);
      }
    }
  }
  traverse(props.data, 0);
  return result;
});

/** 判断节点是否展开 */
function isExpanded(value: string) {
  return expandedKeys.value.has(value);
}

/** 处理节点点击 */
function handleNodeClick(node: FlatNode) {
  emit("click", node.raw);
}

/** 处理节点展开/收起 */
function handleExpand(node: FlatNode) {
  if (!node.hasChildren) return;
  const value = node.value;
  const next = new Set(expandedKeys.value);
  if (next.has(value)) {
    next.delete(value);
  } else {
    next.add(value);
  }
  expandedKeys.value = next;
  emit("expand", node.raw, next.has(value));
}

/** 处理操作按钮点击 */
function handleNodeAction(node: FlatNode) {
  emit("action", node.raw);
}

/** 判断节点是否选中（多选模式） */
function isChecked(value: string) {
  return internalCheckedKeys.value.has(value);
}

/** 判断是否半选状态（部分子节点选中） */
function isIndeterminate(value: string) {
  if (props.checkStrictly) return false;
  const node = findNodeByValue(value, props.data);
  if (!node) return false;
  const children = node[props.childrenKey] as TreeOption[] | undefined;
  if (!children || children.length === 0) return false;

  const childValues = getAllChildValues(children);
  if (childValues.length === 0) return false;

  const checkedCount = childValues.filter((v) => internalCheckedKeys.value.has(v)).length;
  return checkedCount > 0 && checkedCount < childValues.length;
}

/** 根据 value 查找节点 */
function findNodeByValue(value: string, nodes: TreeOption[]): TreeOption | null {
  for (const node of nodes) {
    if (String(node[props.valueKey]) === value) return node;
    const children = node[props.childrenKey] as TreeOption[] | undefined;
    if (children) {
      const found = findNodeByValue(value, children);
      if (found) return found;
    }
  }
  return null;
}

/** 获取所有子节点的 value 数组 */
function getAllChildValues(nodes: TreeOption[]): string[] {
  const result: string[] = [];
  function traverse(list: TreeOption[]) {
    for (const node of list) {
      result.push(String(node[props.valueKey]));
      const children = node[props.childrenKey] as TreeOption[] | undefined;
      if (children) traverse(children);
    }
  }
  traverse(nodes);
  return result;
}

/** 获取所有父节点的 value 数组 */
function getAllParentValues(value: string, nodes: TreeOption[], parents: string[] = []): string[] {
  for (const node of nodes) {
    const nodeValue = String(node[props.valueKey]);
    if (nodeValue === value) return parents;
    const children = node[props.childrenKey] as TreeOption[] | undefined;
    if (children) {
      const found = getAllParentValues(value, children, [...parents, nodeValue]);
      if (found.length > 0) return found;
    }
  }
  return [];
}

/** 处理多选选中状态变化 */
function handleCheck(node: FlatNode) {
  const value = node.value;
  const checked = !internalCheckedKeys.value.has(value);
  const newCheckedKeys = new Set(internalCheckedKeys.value);

  if (checked) {
    newCheckedKeys.add(value);
  } else {
    newCheckedKeys.delete(value);
  }

  // 父子联动
  if (!props.checkStrictly) {
    const children = node.raw[props.childrenKey] as TreeOption[] | undefined;
    // 选中/取消选中所有子节点
    if (children && children.length > 0) {
      const childValues = getAllChildValues(children);
      for (const childValue of childValues) {
        if (checked) {
          newCheckedKeys.add(childValue);
        } else {
          newCheckedKeys.delete(childValue);
        }
      }
    }

    // 更新父节点状态
    const parentValues = getAllParentValues(value, props.data);
    for (const parentValue of parentValues) {
      const parentNode = findNodeByValue(parentValue, props.data);
      if (parentNode) {
        const parentChildren = parentNode[props.childrenKey] as TreeOption[] | undefined;
        if (parentChildren && parentChildren.length > 0) {
          const parentChildValues = getAllChildValues(parentChildren);
          const allChecked = parentChildValues.every((v) => newCheckedKeys.has(v));
          if (allChecked) {
            newCheckedKeys.add(parentValue);
          } else {
            newCheckedKeys.delete(parentValue);
          }
        }
      }
    }
  }

  internalCheckedKeys.value = newCheckedKeys;
  emit("check", Array.from(newCheckedKeys), { checked, node: node.raw });
}

/** 监听数据变化，默认展开全部 */
watch(
  () => props.data,
  (data) => {
    if (props.defaultExpandAll && data.length > 0) {
      const allValues: string[] = [];
      function getAll(nodes: TreeOption[]) {
        for (const node of nodes) {
          const children = node[props.childrenKey] as TreeOption[] | undefined;
          allValues.push(String(node[props.valueKey]));
          if (children && children.length > 0) {
            getAll(children);
          }
        }
      }
      getAll(data);
      expandedKeys.value = new Set(allValues);
    }
  },
  { immediate: true }
);
</script>

<style lang="scss" scoped>
.custom-tree {
  background: var(--color-bg-card);
}

.custom-tree-node {
  &__content {
    display: flex;
    align-items: center;
    min-height: 88rpx;
    padding-right: 24rpx;
    background: var(--color-bg-card);
    border-bottom: 2rpx solid var(--color-border-light);

    &:active {
      background: var(--color-fill-2);
    }
  }

  &__expand {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 48rpx;
    height: 48rpx;
  }

  &__expand-placeholder {
    width: 48rpx;
    height: 48rpx;
  }

  &__checkbox {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    margin-right: 8rpx;
  }

  &__arrow {
    color: var(--color-text-secondary);
    transition: transform 0.2s ease;

    &--expanded {
      transform: rotate(90deg);
    }
  }

  &__label-wrapper {
    display: flex;
    flex: 1;
    gap: 16rpx;
    align-items: center;
    min-width: 0;
  }

  &__label {
    flex: 1;
    overflow: hidden;
    font-size: 28rpx;
    color: var(--color-text);
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__action {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 64rpx;
    height: 64rpx;
    border-radius: 50%;
  }
}
</style>
