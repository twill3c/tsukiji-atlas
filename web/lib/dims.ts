// 時代・分野の表示定義(キーは SPEC §4 が正、gold/contract.py と一致させる)
// 色は dataviz 参照パレットの 7 スロットを時系列順に固定割当。
// validate_palette.js: 隣接ペア全 PASS / 全ペアは 7 色の既知限界で不足 →
// 色単独に依存しない(常時凡例・マーカー白リング・詳細パネルで時代をテキスト表示)。

export const ERAS = [
  { key: "edo_early", label: "江戸前期", color: "#2a78d6" },
  { key: "edo_late", label: "江戸後期", color: "#eb6834" },
  { key: "bakumatsu", label: "幕末", color: "#1baf7a" },
  { key: "meiji", label: "明治", color: "#eda100" },
  { key: "taisho", label: "大正", color: "#e87ba4" },
  { key: "showa", label: "昭和", color: "#008300" },
  { key: "heisei_reiwa", label: "平成以降", color: "#4a3aa7" },
] as const;

export const CATEGORIES = [
  { key: "shrine_temple_church", label: "寺社・教会" },
  { key: "samurai_site", label: "武家地・屋敷跡" },
  { key: "monument_origin", label: "発祥の地・記念碑" },
  { key: "edu_medical", label: "教育・医療" },
  { key: "naval_military", label: "軍事・海軍" },
  { key: "market_food", label: "市場・食文化" },
  { key: "bridge_civil", label: "橋梁・土木" },
  { key: "literature_arts", label: "文学・芸能" },
] as const;

export const ERA_KEYS = ERAS.map((e) => e.key as string);
export const CATEGORY_KEYS = CATEGORIES.map((c) => c.key as string);

export const eraLabel = (key: string): string => ERAS.find((e) => e.key === key)?.label ?? key;
export const eraColor = (key: string): string => ERAS.find((e) => e.key === key)?.color ?? "#898781";
export const categoryLabel = (key: string): string =>
  CATEGORIES.find((c) => c.key === key)?.label ?? key;
