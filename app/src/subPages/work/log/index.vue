<template>
  <view>
    <view>
      <wd-search
        v-model="queryParams.keywords"
        placeholder="搜索日志内容"
        hide-cancel
        @search="handleSearch"
      />
    </view>

    <!-- 日志列表 -->
    <view class="mt-16rpx">
      <wd-card v-for="item in logs" :key="item.id" @click="openLogDetail(item)">
        <!-- 主信息行 -->
        <view class="flex-start">
          <view class="flex-1">
            <view class="flex-start mt-12rpx">
              <text class="font-bold text-32rpx">{{ item.operatorName }}</text>
              <wd-tag
                plain
                size="small"
                class="ml-16rpx"
                :type="item.status === 1 ? 'success' : 'danger'"
              >
                {{ item.status === 1 ? "成功" : "失败" }}
              </wd-tag>
            </view>
            <text class="text-24rpx color-text-secondary truncate">{{ item.title }}</text>
          </view>
        </view>

        <!-- 辅助信息行 -->
        <view class="flex gap-24rpx mt-12rpx">
          <view class="flex-start min-w-0 flex-1">
            <wd-icon name="location" size="16" class="color-text-secondary" />
            <text class="ml-8rpx text-24rpx color-text-secondary">
              {{ item.ip }} {{ item.region }}
            </text>
          </view>
        </view>

        <!-- 元信息行 -->
        <view class="flex-between mt-16rpx">
          <text class="item-time">{{ formatDateTime(item.createTime) }}</text>
          <view
            class="item-action"
            hover-class="item-action--hover"
            @click.stop="openLogDetail(item)"
          >
            <wd-icon name="eye" size="16" class="color-text-secondary" />
          </view>
        </view>
      </wd-card>

      <wd-loadmore v-if="loadMoreState !== 'idle'" :state="loadMoreState" @reload="retry" />
      <wd-empty v-else-if="total === 0" icon="search-line" tip="暂无数据" />
    </view>

    <!-- 详情弹窗 -->
    <wd-popup
      v-model="detailDialog.visible"
      position="bottom"
      custom-class="popup-bottom"
      @close="closeLogDetail"
    >
      <view class="p-4">
        <view class="popup-title">日志详情</view>
        <wd-cell-group border>
          <wd-cell title="操作标题" :value="logDetail.title" />
          <wd-cell title="操作人" :value="logDetail.operatorName" />
          <wd-cell title="操作时间" :value="formatDateTime(logDetail.createTime)" />
          <wd-cell title="状态">
            <template #value>
              <wd-tag :type="logDetail.status === 1 ? 'success' : 'danger'" size="small">
                {{ logDetail.status === 1 ? "成功" : "失败" }}
              </wd-tag>
            </template>
          </wd-cell>
          <wd-cell title="自定义内容" :value="logDetail.content || '无'" />
          <wd-cell title="IP" :value="logDetail.ip" />
          <wd-cell title="地区" :value="logDetail.region" />
          <wd-cell title="请求路径" :value="logDetail.requestUri" />
          <wd-cell title="请求方法" :value="logDetail.requestMethod" />
          <wd-cell title="浏览器" :value="logDetail.browser" />
          <wd-cell title="终端系统" :value="logDetail.os" />
          <wd-cell title="耗时(毫秒)" :value="String(logDetail.executionTime || 0)" />
          <wd-cell v-if="logDetail.errorMsg" title="错误信息" :value="logDetail.errorMsg" />
        </wd-cell-group>
        <view class="popup-actions">
          <wd-button type="info" variant="plain" block @click="closeLogDetail">关闭</wd-button>
        </view>
      </view>
    </wd-popup>
  </view>
</template>

<script lang="ts" setup>
import { onLoad } from "@dcloudio/uni-app";
import { usePagedList } from "@/composables/usePagedList";
import LogAPI, { type LogPageQuery, LogItem } from "@/api/log";
import { formatDateTime } from "@/utils/format";

definePage({
  name: "log",
  style: { navigationBarTitleText: "系统日志", enablePullDownRefresh: true },
});

const queryParams = reactive<LogPageQuery>({ pageNum: 1, pageSize: 10 });

// 分页加载（触底加载 + 下拉刷新统一由 usePagedList 维护）
const {
  items: logs,
  total,
  loadMoreState,
  reload,
  retry,
} = usePagedList(LogAPI.getPage, queryParams);

const logDetail = ref<LogItem>({});
const detailDialog = reactive({ visible: false });

// 搜索触发
const handleSearch = () => loadLogList();

// 加载列表（回到第一页）
function loadLogList() {
  reload();
}

// 打开详情弹窗
function openLogDetail(item: LogItem) {
  logDetail.value = item;
  detailDialog.visible = true;
}

// 关闭详情弹窗
function closeLogDetail() {
  detailDialog.visible = false;
}

onLoad(() => {
  loadLogList();
});
</script>

<script lang="ts">
export default { options: { styleIsolation: "shared" } };
</script>
