// F-07: 詳細パネルの表示整形。欠落・分岐はすべてここで吸収する純関数(T-043)
import { categoryLabel, eraLabel } from "./dims";
import type { SiteProps } from "./types";

const LICENSE_TEXT: Record<string, string> = {
  self: "自前調査・執筆",
  CC0: "CC0(Wikidata)",
  "CC BY 4.0": "CC BY 4.0(東京都オープンデータ)",
};

const SOURCE_LABEL: Record<string, string> = {
  wikidata: "Wikidata",
  tokyo_od: "東京都オープンデータ",
  curated: "手動調査",
};

export type DetailView = {
  name: string;
  eraLabel: string;
  categoryLabel: string;
  yearText: string;
  summary: string;
  sourceLabel: string;
  licenseText: string;
  qid?: string;
};

export function formatDetail(props: SiteProps): DetailView {
  return {
    name: props.name,
    eraLabel: eraLabel(props.era),
    categoryLabel: categoryLabel(props.category),
    yearText: props.year != null ? `${props.year}年` : "年代不詳",
    summary: props.summary,
    sourceLabel: SOURCE_LABEL[props.source] ?? props.source,
    licenseText: LICENSE_TEXT[props.license] ?? props.license,
    qid: props.qid,
  };
}
