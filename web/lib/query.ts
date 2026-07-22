// F-06: 状態は URL クエリに持つ(?era=meiji,bakumatsu&cat=monument_origin)。
// 共有可能な絞り込みのため、往復変換は不変(T-042)。未知キーは黙って除去し、
// 並びは定義順に正準化する。
import { CATEGORY_KEYS, ERA_KEYS } from "./dims";
import type { FilterState } from "./types";

function canonicalize(values: string[], order: string[]): string[] {
  const set = new Set(values);
  return order.filter((k) => set.has(k));
}

export function parseQuery(search: string): FilterState {
  const params = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  const split = (v: string | null) => (v ? v.split(",").filter(Boolean) : []);
  return {
    eras: canonicalize(split(params.get("era")), ERA_KEYS),
    cats: canonicalize(split(params.get("cat")), CATEGORY_KEYS),
  };
}

export function buildQuery(state: FilterState): string {
  const parts: string[] = [];
  if (state.eras.length > 0) parts.push(`era=${canonicalize(state.eras, ERA_KEYS).join(",")}`);
  if (state.cats.length > 0) parts.push(`cat=${canonicalize(state.cats, CATEGORY_KEYS).join(",")}`);
  return parts.length > 0 ? `?${parts.join("&")}` : "";
}
