<template>
  <view>
    <custom-navbar title="工作台" :show-back="false" placeholder />
    <!-- tabbar 壳为全出血（index/mine 的沉浸式头需要贴边），工作台网格用工具类补齐
         横向 32rpx / 顶部 16rpx，与 default 壳的 .page 内边距保持一致 -->
    <view class="px-32rpx pt-16rpx">
      <template v-for="(item, index) in visibleGridList" :key="index">
        <wd-card :title="item.title">
          <wd-grid clickable :column="4">
            <wd-grid-item
              v-for="(child, childIndex) in item.children"
              :key="childIndex"
              use-slot
              @click="handleNavClick(child)"
            >
              <view class="p-2">
                <image class="w-72rpx h-72rpx rounded-8rpx" :src="child.icon" />
              </view>
              <view>{{ child.title }}</view>
            </wd-grid-item>
          </wd-grid>
        </wd-card>
      </template>
    </view>
  </view>
</template>

<script lang="ts" setup>
import { computed } from "vue";
import { useNavigation } from "@/composables/useNavigation";
import { workMenuGroups } from "@/config/work-menu";
import { hasPermission as checkPermission } from "@/utils/permission";

definePage({
  name: "work",
  style: {
    navigationStyle: "custom",
    navigationBarTitleText: "工作台",
  },
  layout: "tabbar",
});

const { handleNavClick } = useNavigation();

// 检查是否有权限
const hasPermission = (perm: string) => {
  if (!perm) return true;
  return checkPermission(perm);
};

// 根据权限过滤后的菜单列表
const visibleGridList = computed(() => {
  return workMenuGroups
    .map((group) => ({
      ...group,
      children: group.children.filter((item) => hasPermission(item.perm)),
    }))
    .filter((group) => group.children.length > 0);
});
</script>
