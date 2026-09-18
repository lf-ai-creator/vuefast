import { ref } from "vue";
import { useToast, useDialog } from "@wot-ui/ui";

/** 操作菜单项：name 用于展示，handler 选中后执行 */
export interface ActionMenuOption {
  name: string;
  color?: string;
  handler: () => void | Promise<void>;
}

/**
 * 列表页「更多操作」菜单（wd-action-sheet）统一逻辑
 *
 * 页面只需声明菜单项（含权限判断），选中分发与空菜单提示由这里处理：
 *
 * const { actionSheetVisible, actionSheetActions, showActions, handleActionSelect, confirmAction } =
 *   useActionSheet();
 */
export function useActionSheet() {
  const toast = useToast();
  const { confirm } = useDialog();

  const actionSheetVisible = ref(false);
  const actionSheetActions = ref<{ name: string; color?: string }[]>([]);
  let handlers: Record<string, () => void> = {};

  /** 展示操作菜单，无可用项时提示「暂无操作权限」 */
  function showActions(menus: ActionMenuOption[]) {
    if (menus.length === 0) {
      toast.warning("暂无操作权限");
      return;
    }
    actionSheetActions.value = menus.map(({ name, color }) => ({ name, color }));
    handlers = Object.fromEntries(menus.map((menu) => [menu.name, menu.handler]));
    actionSheetVisible.value = true;
  }

  function handleActionSelect({ item }: { item: { name: string } }) {
    handlers[item.name]?.();
  }

  /**
   * 标准危险操作确认流程：确认弹窗 → 执行 → 成功提示，用户取消静默
   *
   * @param options.msg 确认弹窗提示文案
   * @param options.action 确认后执行的操作
   * @param options.title 确认弹窗标题，默认「确认删除」
   * @param options.successText 成功提示文案，默认「删除成功」
   */
  async function confirmAction(options: {
    msg: string;
    action: () => Promise<void>;
    title?: string;
    successText?: string;
  }) {
    const { msg, action, title = "确认删除", successText = "删除成功" } = options;
    try {
      await confirm({ title, msg, headerImage: "warning" });
      await action();
      toast.success(successText);
    } catch {
      // 用户取消操作
    }
  }

  return { actionSheetVisible, actionSheetActions, showActions, handleActionSelect, confirmAction };
}
