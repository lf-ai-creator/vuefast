/**
 * 沿选项树深度优先查找目标节点的完整节点链（含自身）
 *
 * 值比较统一转为字符串，兼容选项值为 number、目标值为 string（或相反）的场景
 *
 * @param options 选项树，如部门选项
 * @param targetValue 目标节点值
 * @returns 从根到目标的节点链，未命中返回 null
 */
export function findOptionChain(
  options: OptionType[],
  targetValue: string | number
): OptionType[] | null {
  for (const option of options) {
    if (String(option.value) === String(targetValue)) {
      return [option];
    }
    if (option.children?.length) {
      const chain = findOptionChain(option.children, targetValue);
      if (chain) {
        return [option, ...chain];
      }
    }
  }
  return null;
}
