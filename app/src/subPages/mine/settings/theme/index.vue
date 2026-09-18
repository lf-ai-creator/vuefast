<template>
  <view>
    <!-- 暗黑模式设置 -->
    <wd-cell-group title="外观模式" border>
      <wd-cell title="暗黑模式" :value="isDark ? '已开启' : '已关闭'">
        <wd-switch :model-value="isDark" @change="handleToggleDarkMode" />
      </wd-cell>
    </wd-cell-group>

    <!-- 主题色设置 -->
    <wd-cell-group title="主题色彩" border custom-class="mt-24rpx">
      <!-- 预设颜色选择 -->
      <wd-cell title="预设主题色">
        <template #default>
          <view class="flex flex-wrap gap-12rpx">
            <view
              v-for="(color, index) in themeColorOptions"
              :key="index"
              class="color-option"
              :class="{ 'color-option--active': currentPrimaryColor === color.primary }"
              :style="{ backgroundColor: color.primary }"
              @click="handleSelectColor(color)"
            >
              <wd-icon
                v-if="currentPrimaryColor === color.primary"
                name="check"
                size="14"
                color="var(--color-text-inverse)"
              />
            </view>
          </view>
        </template>
      </wd-cell>

      <!-- 当前主题色 -->
      <wd-cell title="当前主题色">
        <template #default>
          <view class="flex items-center gap-12rpx">
            <view
              class="w-32rpx h-32rpx rounded-full"
              :style="{ backgroundColor: currentPrimaryColor }"
            />
            <text class="text-24rpx color-text-secondary">{{ currentPrimaryColor }}</text>
          </view>
        </template>
      </wd-cell>

      <!-- 自定义颜色 -->
      <wd-cell title="自定义颜色" is-link @click="showCustomInput">
        <template #icon>
          <wd-icon name="edit" size="16" class="mr-12rpx" />
        </template>
      </wd-cell>
    </wd-cell-group>

    <!-- 效果预览 -->
    <wd-cell-group title="效果预览" border custom-class="mt-24rpx">
      <wd-cell>
        <template #default>
          <view class="flex w-full items-center justify-center gap-24rpx py-12rpx">
            <wd-button size="small">主要按钮</wd-button>
            <text class="text-28rpx font-500" :style="{ color: currentPrimaryColor }">
              主题色文本
            </text>
            <wd-tag type="primary" size="small" variant="filled">标签</wd-tag>
          </view>
        </template>
      </wd-cell>
    </wd-cell-group>

    <!-- 操作按钮 -->
    <view class="mt-32rpx">
      <wd-button plain size="large" block @click="handleResetTheme">重置为默认主题</wd-button>
    </view>

    <!-- 自定义颜色输入弹窗 -->
    <wd-popup v-model="showCustomColorInput" position="bottom" custom-class="popup-bottom">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-header__title">自定义主题色</text>
          <view
            class="w-64rpx h-64rpx flex-center rounded-full"
            hover-class="bg-[var(--color-text-placeholder)]/16"
            @click="showCustomColorInput = false"
          >
            <wd-icon name="close" size="18" class="color-text-secondary" />
          </view>
        </view>

        <view class="p-4">
          <text class="text-28rpx color-text-secondary">请输入十六进制颜色值</text>
          <view class="flex items-center gap-16rpx mt-16rpx">
            <view
              class="flex-shrink-0 w-48rpx h-48rpx rounded-8rpx"
              :style="{ backgroundColor: customColor || currentPrimaryColor }"
            />
            <wd-input
              v-model="customColor"
              placeholder="例如: #F53F3F"
              :maxlength="7"
              custom-class="theme-input"
            />
          </view>
          <text class="text-24rpx color-text-placeholder mt-12rpx">支持格式：#RGB 或 #RRGGBB</text>
        </view>

        <view class="popup-footer">
          <wd-button type="info" plain @click="showCustomColorInput = false">取消</wd-button>
          <wd-button @click="applyCustomColor">应用</wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script lang="ts" setup>
import { useTheme } from "@/composables/useTheme";
import { useToast, useDialog } from "@wot-ui/ui";

definePage({
  name: "theme",
  style: { navigationBarTitleText: "主题设置" },
});

// 使用主题组合函数
const { isDark, themeColorOptions, toggleThemeMode, setThemeColor, selectedThemeColor } =
  useTheme();

const toast = useToast();
const { confirm } = useDialog();

// 自定义颜色输入
const customColor = ref("");
const showCustomColorInput = ref(false);

// 当前生效的主题色主色
const currentPrimaryColor = computed(() => selectedThemeColor.value.primary);

// 选择预设颜色
const handleSelectColor = (color: (typeof themeColorOptions)[0]) => {
  setThemeColor(color);
  customColor.value = color.primary;
  toast.success("主题色已更新");
};

// 显示自定义颜色输入
const showCustomInput = () => {
  showCustomColorInput.value = true;
  customColor.value = currentPrimaryColor.value;
};

// 应用自定义颜色
const applyCustomColor = () => {
  // 验证颜色格式
  const colorRegex = /^#([0-9A-F]{6}|[0-9A-F]{3})$/i;
  if (!colorRegex.test(customColor.value)) {
    toast.error("请输入有效的颜色值");
    return;
  }

  // 3 位色值展开为 6 位（#ABC → #AABBCC）
  let color = customColor.value;
  if (color.length === 4) {
    color = `#${color[1]}${color[1]}${color[2]}${color[2]}${color[3]}${color[3]}`;
  }

  setThemeColor({ name: "自定义", value: "custom", primary: color });
  showCustomColorInput.value = false;
  toast.success("自定义主题色已应用");
};

// 重置为默认主题
const handleResetTheme = async () => {
  try {
    await confirm({ title: "确认重置", msg: "确定要重置为默认主题吗？", headerImage: "warning" });
    setThemeColor(themeColorOptions[0]);
    customColor.value = themeColorOptions[0].primary;
    toast.success("已重置为默认主题");
  } catch {
    // 用户取消
  }
};

// 切换暗黑模式
const handleToggleDarkMode = () => {
  toggleThemeMode();
  toast.success(`已切换到${isDark.value ? "暗黑" : "浅色"}模式`);
};

// 页面显示时同步输入框回显（首次进入同样触发）
onShow(() => {
  customColor.value = currentPrimaryColor.value;
});
</script>

<style lang="scss" scoped>
.color-option {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48rpx;
  height: 48rpx;
  cursor: pointer;
  border-radius: 50%;

  &--active {
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.2);
    transform: scale(1.1);
  }
}

.popup-content {
  padding-bottom: env(safe-area-inset-bottom);
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  border-bottom: 1rpx solid var(--color-border);
}

.popup-header__title {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--color-text);
}

.popup-footer {
  display: flex;
  gap: 24rpx;
  padding: 24rpx 32rpx;
  border-top: 1rpx solid var(--color-border);
}

// 自定义颜色输入框：跟随项目填充色与文字色（wot 默认 filled-oppo / text-main）
:deep(.theme-input) {
  --wot-input-bg: var(--color-fill-1);
  --wot-input-inner-color: var(--color-text);
}
</style>
