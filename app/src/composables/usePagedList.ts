import { ref, type Ref } from "vue";
import { onPullDownRefresh, onReachBottom } from "@dcloudio/uni-app";

/**
 * 分页列表统一逻辑：触底加载 + 下拉刷新
 *
 * 页面只维护业务筛选条件；页码推进、加载状态和列表数据全部由这里接管。
 * 每次请求前对筛选条件做快照，并携带请求序号：快速切换搜索条件时，
 * 旧请求的晚到响应会被直接丢弃，不会覆盖新条件的结果。
 *
 * 底部状态 loadMoreState 的含义：
 * - loading：任一请求进行中
 * - error：最近一次请求失败（点击可重试当前失败页）
 * - finished：已加载全部数据（底部显示"没有更多了"）
 * - idle：无底部指示（空列表或还有下一页待触底）
 *
 * const { items, total, loadMoreState, reload, retry } = usePagedList(UserAPI.getPage, queryParams);
 */
export function usePagedList<T, Q extends { pageNum: number; pageSize: number }>(
  fetcher: (query: Q) => Promise<{ list: T[]; total: number }>,
  queryParams: Q
) {
  const total = ref(0);
  const items = ref<T[]>([]) as Ref<T[]>;
  const loadMoreState = ref<"loading" | "error" | "finished" | "idle">("loading");

  /** 已成功加载的页数，下一页 = loadedPages + 1 */
  let loadedPages = 0;
  /** 请求序号：序号不匹配的响应一律丢弃 */
  let requestSeq = 0;
  /** 最近一次请求的目标页与写入方式，供失败重试 */
  let lastAttempt: { page: number; append: boolean } | null = null;

  /** 组装第 page 页的请求参数：快照 + 页码，避免请求期间筛选对象继续变化 */
  function buildQuery(page: number): Q {
    return { ...queryParams, pageNum: page };
  }

  /** 已加载数量是否小于总数 */
  function hasMore(): boolean {
    return items.value.length < total.value;
  }

  /**
   * 拉取第 page 页；append 为触底追加，否则整体替换（首次加载/重新搜索）
   * keepOnFail 为 true 时（下拉刷新）失败保留现有数据，否则替换失败清空列表展示错误态
   */
  async function fetchPage(page: number, append: boolean, keepOnFail = false): Promise<void> {
    const seq = ++requestSeq;
    lastAttempt = { page, append };
    loadMoreState.value = "loading";
    try {
      const data = await fetcher(buildQuery(page));
      if (seq !== requestSeq) return; // 过期响应：已被更新的请求接管
      items.value = append ? [...items.value, ...data.list] : data.list;
      total.value = data.total;
      loadedPages = page;
      loadMoreState.value = items.value.length === 0 || hasMore() ? "idle" : "finished";
    } catch {
      if (seq !== requestSeq) return;
      if (!append && !keepOnFail) {
        items.value = [];
        total.value = 0;
      }
      loadMoreState.value = "error";
    }
  }

  /** 回到第一页重新拉取（搜索/筛选/增删改后调用），返回 Promise 可等待刷新完成 */
  async function reload(): Promise<void> {
    loadedPages = 0;
    await fetchPage(1, false);
  }

  /** 重试最近一次失败的请求：页码与写入方式保持不变，追加失败保留已有列表 */
  function retry(): void {
    if (!lastAttempt) return;
    fetchPage(lastAttempt.page, lastAttempt.append);
  }

  // 触底加载下一页：请求进行中不重复触发，防止并发追加
  onReachBottom(() => {
    if (loadMoreState.value === "loading") return;
    if (hasMore()) {
      fetchPage(loadedPages + 1, true);
    }
  });

  // 下拉刷新：回到第一页；失败保留现有数据，请求序号防止与触底请求交叉写入
  onPullDownRefresh(async () => {
    try {
      await fetchPage(1, false, true);
    } finally {
      uni.stopPullDownRefresh();
    }
  });

  return { items, total, loadMoreState, reload, retry };
}
