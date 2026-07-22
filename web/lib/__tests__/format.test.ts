// T-043(F-07): 詳細パネルのデータ整形 — year 欠落時の表示、license 表記の分岐
import { describe, expect, it } from "vitest";

import { formatDetail } from "../format";
import type { SiteProps } from "../types";

const base: SiteProps = {
  site_id: "tsukiji-akashicho-004",
  name: "慶應義塾発祥の地記念碑",
  era: "bakumatsu",
  category: "edu_medical",
  year: 1858,
  summary: "福澤諭吉が開いた蘭学塾に始まる。",
  source: "curated",
  license: "self",
  area: "tsukiji-akashicho",
};

describe("formatDetail (T-043)", () => {
  it("year がある場合は西暦表示、era・category は表示名に変換", () => {
    const d = formatDetail(base);
    expect(d.yearText).toBe("1858年");
    expect(d.eraLabel).toBe("幕末");
    expect(d.categoryLabel).toBe("教育・医療");
  });

  it("year 欠落時は「年代不詳」", () => {
    expect(formatDetail({ ...base, year: undefined }).yearText).toBe("年代不詳");
  });

  it("license 表記の分岐(self / CC0 / CC BY 4.0)", () => {
    expect(formatDetail(base).licenseText).toBe("自前調査・執筆");
    expect(formatDetail({ ...base, source: "wikidata", license: "CC0" }).licenseText).toBe("CC0(Wikidata)");
    expect(formatDetail({ ...base, source: "tokyo_od", license: "CC BY 4.0" }).licenseText).toBe(
      "CC BY 4.0(東京都オープンデータ)",
    );
  });

  it("source の表示名", () => {
    expect(formatDetail(base).sourceLabel).toBe("手動調査");
    expect(formatDetail({ ...base, source: "wikidata" }).sourceLabel).toBe("Wikidata");
  });
});
