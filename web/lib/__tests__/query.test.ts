// T-042(F-06): URL クエリ ↔ フィルタ状態の相互変換(往復で不変)
import { describe, expect, it } from "vitest";

import { buildQuery, parseQuery } from "../query";

describe("parseQuery / buildQuery (T-042)", () => {
  it("roundtrip: 状態 → クエリ → 状態 が不変", () => {
    const states = [
      { eras: [], cats: [] },
      { eras: ["meiji"], cats: [] },
      { eras: ["bakumatsu", "meiji"], cats: ["monument_origin"] },
      { eras: ["edo_early", "showa", "heisei_reiwa"], cats: ["market_food", "bridge_civil"] },
    ];
    for (const state of states) {
      expect(parseQuery(buildQuery(state))).toEqual(state);
    }
  });

  it("roundtrip: クエリ → 状態 → クエリ が不変(GUIDE §5 の例)", () => {
    const q = "?era=bakumatsu,meiji&cat=monument_origin";
    expect(buildQuery(parseQuery(q))).toBe(q);
  });

  it("キーの並びは定義順に正準化される", () => {
    expect(parseQuery("?era=meiji,bakumatsu")).toEqual({ eras: ["bakumatsu", "meiji"], cats: [] });
  });

  it("未定義キーと重複は黙って除去", () => {
    expect(parseQuery("?era=meiji,meiji,atlantis&cat=bogus")).toEqual({ eras: ["meiji"], cats: [] });
  });

  it("空状態はクエリなし", () => {
    expect(buildQuery({ eras: [], cats: [] })).toBe("");
  });
});
