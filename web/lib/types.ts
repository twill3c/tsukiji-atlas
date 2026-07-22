// Gold 契約(SPEC §5)の properties。web 側はこの型だけを信頼する
export type SiteProps = {
  site_id: string;
  name: string;
  era: string;
  category: string;
  year?: number;
  summary: string;
  source: "wikidata" | "tokyo_od" | "curated" | string;
  license: "CC0" | "CC BY 4.0" | "self" | string;
  area: string;
  qid?: string;
};

export type SiteFeature = {
  type: "Feature";
  geometry: { type: "Point"; coordinates: [number, number] }; // [経度, 緯度]
  properties: SiteProps;
};

export type FilterState = {
  eras: string[]; // 定義順に正準化して保持
  cats: string[];
};
