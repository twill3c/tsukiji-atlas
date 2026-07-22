// T-041(F-06): フィルタロジック — era/category の AND-of-OR 絞り込み
import { describe, expect, it } from "vitest";

import { matchesFilter } from "../filter";
import type { SiteProps } from "../types";

const site = (era: string, category: string): SiteProps => ({
  site_id: "tsukiji-akashicho-001",
  name: "テスト地物",
  era,
  category,
  summary: "要約。",
  source: "curated",
  license: "self",
  area: "tsukiji-akashicho",
});

describe("matchesFilter (T-041)", () => {
  it("フィルタが空なら全件通す", () => {
    expect(matchesFilter(site("meiji", "monument_origin"), { eras: [], cats: [] })).toBe(true);
  });

  it("era のみ: OR で絞る", () => {
    const state = { eras: ["meiji", "bakumatsu"], cats: [] };
    expect(matchesFilter(site("meiji", "edu_medical"), state)).toBe(true);
    expect(matchesFilter(site("bakumatsu", "edu_medical"), state)).toBe(true);
    expect(matchesFilter(site("showa", "edu_medical"), state)).toBe(false);
  });

  it("category のみ: OR で絞る", () => {
    const state = { eras: [], cats: ["bridge_civil", "market_food"] };
    expect(matchesFilter(site("showa", "bridge_civil"), state)).toBe(true);
    expect(matchesFilter(site("showa", "shrine_temple_church"), state)).toBe(false);
  });

  it("era と category の両方: AND-of-OR", () => {
    const state = { eras: ["meiji"], cats: ["edu_medical"] };
    expect(matchesFilter(site("meiji", "edu_medical"), state)).toBe(true);
    expect(matchesFilter(site("meiji", "bridge_civil"), state)).toBe(false); // era 合致でも cat 不合致
    expect(matchesFilter(site("showa", "edu_medical"), state)).toBe(false); // cat 合致でも era 不合致
  });
});
