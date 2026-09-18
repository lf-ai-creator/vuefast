<template>
  <view>
    <!-- 轮播图 -->
    <view class="relative">
      <wd-swiper
        v-model:current="activeSlideIndex"
        custom-class="swiper-box"
        :list="swiperList"
        autoplay
      />
      <view class="hero-fade"></view>
    </view>

    <!-- 快捷导航 -->
    <view class="quick-nav-card">
      <wd-grid clickable :column="4">
        <wd-grid-item
          v-for="(item, index) in quickNavList"
          :key="index"
          use-slot
          @click="handleNavClickWithGuard(item)"
        >
          <view class="quick-nav-card__item">
            <image class="quick-nav-card__icon" :src="item.icon" mode="aspectFit" />
            <text class="quick-nav-card__label">{{ item.title }}</text>
          </view>
        </wd-grid-item>
      </wd-grid>
    </view>

    <!-- 通知公告 -->
    <view class="notice-bar m-24rpx" @click="handleNoticeClick">
      <view class="notice-bar__icon">
        <wd-icon name="check" size="32rpx" color="var(--color-success)" />
      </view>
      <view class="notice-bar__content">
        <text class="notice-bar__text">{{ noticeText || "暂无通知公告" }}</text>
      </view>
    </view>

    <!-- 数据统计 -->
    <view class="grid grid-cols-2 gap-16rpx m-24rpx">
      <view class="stat-card stat-card--uv">
        <image class="stat-card__icon" src="/static/icons/uv.svg" mode="aspectFit" />
        <view class="stat-card__header">
          <text class="stat-card__label">访客数</text>
          <view class="stat-card__dot"></view>
        </view>
        <text class="stat-card__num">{{ visitOverviewData.todayUvCount }}</text>
      </view>
      <view class="stat-card">
        <image class="stat-card__icon" src="/static/icons/pv.svg" mode="aspectFit" />
        <view class="stat-card__header">
          <text class="stat-card__label">浏览量</text>
          <view class="stat-card__dot"></view>
        </view>
        <text class="stat-card__num">{{ visitOverviewData.todayPvCount }}</text>
      </view>
    </view>

    <!-- 访问趋势图表 -->
    <view class="chart-wrapper m-24rpx">
      <view class="chart-wrapper__header">
        <text class="chart-wrapper__title">访问趋势</text>
        <view class="segment-control">
          <view
            class="segment-control__item"
            :class="{ 'is-active': trendDays === 7 }"
            @click="switchRange(7)"
          >
            近7天
          </view>
          <view
            class="segment-control__item"
            :class="{ 'is-active': trendDays === 15 }"
            @click="switchRange(15)"
          >
            近15天
          </view>
        </view>
      </view>
      <view class="w-full h-600rpx px-20rpx box-border">
        <qiun-data-charts
          type="area"
          :chartData="chartData"
          :opts="chartOpts"
          background="transparent"
          :canvas2d="true"
        />
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import dayjs from "dayjs";
import { onReady, onShow } from "@dcloudio/uni-app";
import { useThemeStore, useUserStore } from "@/store";
import { useNavigation } from "@/composables/useNavigation";
import { workMenuGroups } from "@/config/work-menu";
import { hasPermission } from "@/utils/permission";
import LogAPI, { type VisitOverview, type VisitTrend } from "@/api/log";
import NoticeAPI, { type NoticeItem } from "@/api/notice";

definePage({
  name: "home",
  style: { navigationStyle: "custom" },
  layout: "tabbar",
});

interface NavItem {
  icon: string;
  title: string;
  url: string;
  perm: string;
}

const userStore = useUserStore();
const themeStore = useThemeStore();
const { handleNavClick } = useNavigation();

const activeSlideIndex = ref(0);
const trendDays = ref(7);

const swiperList = ref(["https://www.youlai.tech/storage/youlai/bg02.png"]);

/** 访问概览数据 */
const visitOverviewData = ref<VisitOverview>({
  todayUvCount: 0,
  todayPvCount: 0,
} as VisitOverview);

/** 通知公告文本 */
const noticeList = ref<NoticeItem[]>([]);
const noticeText = computed(() => {
  const titles = noticeList.value
    .map((n: NoticeItem) => n.title)
    .filter(Boolean)
    .slice(0, 2);
  return titles.length ? titles.join("    ") : "暂无通知";
});

const userPerms = computed(() => userStore.userInfo?.perms || []);
const isAuthenticated = computed(() => userStore.isAuthenticated);
const hasAnyPerm = computed(() => userPerms.value.length > 0);

/** 默认菜单（未登录时显示） */
const defaultNavList = computed(() => {
  const result: NavItem[] = [];
  for (const group of workMenuGroups) {
    for (const item of group.children) {
      result.push(item);
      if (result.length >= 4) return result;
    }
  }
  return result;
});

/** 快捷入口：已登录按权限过滤，未登录显示默认菜单 */
const quickNavList = computed(() => {
  if (!isAuthenticated.value || !hasAnyPerm.value) return defaultNavList.value;
  const result: NavItem[] = [];
  for (const group of workMenuGroups) {
    for (const item of group.children) {
      if (hasPermission(item.perm)) result.push(item);
      if (result.length >= 4) return result;
    }
  }
  return result;
});

const chartData = ref({});
const chartOpts = computed(() => ({
  // canvas 不认 CSS 变量，系列色与轴标签色按选中色/主题取值
  color: [themeStore.selectedThemeColor.primary],
  padding: [20, 0, 20, 0],
  fontColor: themeStore.isDark ? "#a9aeb8" : "#666666",
  xAxis: { fontSize: 10, rotateLabel: true, rotateAngle: 30 },
  yAxis: { disabled: true },
  extra: {
    area: {
      type: "curve",
      opacity: 0.2,
      addLine: true,
      width: 2,
      gradient: true,
      activeType: "hollow",
    },
  },
}));

/** 加载通知公告 */
async function loadNoticeData() {
  if (!isAuthenticated.value) {
    noticeList.value = [];
    return;
  }
  try {
    const { list } = await NoticeAPI.getMyNoticePage({ pageNum: 1, pageSize: 2 });
    noticeList.value = list || [];
  } catch {
    noticeList.value = [];
  }
}

/** 加载访问概览统计 */
function loadVisitOverviewData() {
  LogAPI.getVisitOverview()
    .then((data) => (visitOverviewData.value = data))
    .catch(() => {});
}

/** 加载访问趋势图表 */
async function loadVisitTrendData() {
  const endDate = dayjs().format("YYYY-MM-DD");
  const startDate = dayjs()
    .subtract(trendDays.value - 1, "day")
    .format("YYYY-MM-DD");
  try {
    const data: VisitTrend = await LogAPI.getVisitTrend({ startDate, endDate });
    chartData.value = JSON.parse(
      JSON.stringify({
        categories: (data.dates || []).map((d) => dayjs(d).format("MM-DD")),
        series: [
          { name: "访客数", data: data.uvList || [] },
          { name: "浏览量", data: data.pvList || [] },
        ],
      })
    );
  } catch {
    chartData.value = { categories: [], series: [] };
  }
}

/** 快捷导航点击（未登录跳转登录） */
function handleNavClickWithGuard(item: NavItem) {
  if (!isAuthenticated.value || !hasAnyPerm.value) {
    uni.navigateTo({ url: "/pages/login/index" });
    return;
  }
  handleNavClick(item);
}

/** 跳转通知公告列表 */
function handleNoticeClick() {
  uni.navigateTo({ url: "/subPages/work/notice/index" });
}

/** 切换趋势时间范围 */
function switchRange(value: number) {
  if (trendDays.value === value) return;
  trendDays.value = value;
  loadVisitTrendData();
}

onReady(() => {
  loadNoticeData();
});

// onShow 首次进入同样触发，统一在此加载统计数据（切回 tab 时自动刷新）
onShow(() => {
  loadVisitOverviewData();
  loadVisitTrendData();
});
</script>

<!-- 非 scoped：覆盖 wd-swiper 内部节点高度 -->
<style lang="scss">
.swiper-box,
.swiper-box .wd-swiper__item,
.swiper-box image {
  height: 420rpx;
}
</style>

<style lang="scss" scoped>
.hero-fade {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: var(--z-sticky);
  height: 120rpx;
  pointer-events: none;
  background: linear-gradient(
    to bottom,
    transparent 0%,
    var(--color-bg-page) 60%,
    var(--color-bg-page) 100%
  );
}

.chart-wrapper {
  box-sizing: border-box;
  overflow: hidden;
  background: var(--color-bg-card);
  border: 1rpx solid var(--color-border);
  border-radius: 16rpx;
  box-shadow: var(--shadow-sm);

  &__header {
    display: flex;
    gap: 24rpx;
    align-items: center;
    justify-content: space-between;
    padding: 24rpx 20rpx;
  }

  &__title {
    font-size: 28rpx;
    font-weight: 600;
    color: var(--color-text);
  }
}

.segment-control {
  display: inline-flex;
  align-items: center;
  padding: 4rpx;
  background: var(--color-fill-1);
  border: 1rpx solid var(--color-border);
  border-radius: 12rpx;
}

.segment-control__item {
  padding: 8rpx 20rpx;
  font-size: 24rpx;
  font-weight: 500;
  color: var(--color-text-secondary);
  border-radius: 8rpx;
  transition: all 0.2s ease;
}

.segment-control__item.is-active {
  color: var(--color-text-inverse);
  background: var(--color-primary);
}

.quick-nav-card {
  position: relative;
  z-index: var(--z-sticky);
  padding: 18rpx 8rpx;
  margin: 24rpx;
  margin-top: -120rpx;
  overflow: hidden;
  background: var(--color-bg-card);
  border-radius: 24rpx;
  box-shadow: var(--shadow-md);
  /* 网格项背景交给卡片本身，避免 wot 深色模式默认黑底 */
  --wot-grid-item-bg: transparent;

  &__item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16rpx;
  }

  &__icon {
    width: 72rpx;
    height: 72rpx;
    border-radius: 16rpx;
  }

  &__label {
    margin-top: 12rpx;
    font-size: 24rpx;
    color: var(--color-text);
  }
}

.notice-bar {
  display: flex;
  align-items: center;
  padding: 24rpx 24rpx 24rpx 20rpx;
  background: var(--color-bg-card);
  border: 1rpx solid var(--color-border);
  border-radius: 16rpx;
  box-shadow: var(--shadow-sm);

  &__icon {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 48rpx;
    height: 48rpx;
    margin-right: 16rpx;
    background: var(--color-success-light);
    border-radius: 12rpx;
  }

  &__content {
    flex: 1;
    overflow: hidden;
  }

  &__text {
    display: -webkit-box;
    overflow: hidden;
    font-size: 26rpx;
    font-weight: 500;
    color: var(--color-text);
    -webkit-line-clamp: 1;
    line-clamp: 1;
    -webkit-box-orient: vertical;
  }
}

.stat-card {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 24rpx 20rpx;
  overflow: hidden;
  background: var(--color-bg-card);
  border: 1rpx solid var(--color-border);
  border-radius: 16rpx;
  box-shadow: var(--shadow-sm);
  /* 数字与圆点统一取 --accent，访客数用 --uv 换成绿色 */
  --accent: var(--color-primary);
  --accent-glow: rgba(77, 128, 240, 0.3);

  &--uv {
    --accent: var(--color-success);
    --accent-glow: rgba(52, 209, 157, 0.35);
  }

  &__header {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16rpx;
  }

  &__label {
    font-size: 24rpx;
    font-weight: 500;
    color: var(--color-text-secondary);
  }

  &__icon {
    position: absolute;
    right: 4px;
    bottom: 4px;
    width: 72rpx;
    height: 72rpx;
    opacity: 0.25;
  }

  &__dot {
    width: 12rpx;
    height: 12rpx;
    background: var(--accent);
    border-radius: 50%;
    box-shadow: 0 0 10rpx var(--accent-glow);
  }

  &__num {
    position: relative;
    font-size: 48rpx;
    font-weight: 700;
    line-height: 1;
    color: var(--accent);
    letter-spacing: -1rpx;
  }
}
</style>
