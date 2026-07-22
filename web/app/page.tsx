"use client";

// 状態は URL クエリが正(F-06)。静的エクスポートのため useSearchParams は使わず
// window.location を直接読み書きする(サーバ描画時は空状態で初期化)。
import { useEffect, useMemo, useState } from "react";

import Attribution from "@/components/Attribution";
import DetailPanel from "@/components/DetailPanel";
import FilterChips from "@/components/FilterChips";
import MapView from "@/components/MapView";
import { filterFeatures } from "@/lib/filter";
import { buildQuery, parseQuery } from "@/lib/query";
import type { FilterState, SiteFeature } from "@/lib/types";

export default function Page() {
  const [features, setFeatures] = useState<SiteFeature[]>([]);
  const [filter, setFilter] = useState<FilterState>({ eras: [], cats: [] });
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    setFilter(parseQuery(window.location.search));
    fetch("data/sites.geojson")
      .then((r) => r.json())
      .then((fc) => setFeatures(fc.features as SiteFeature[]))
      .catch(() => setFeatures([]));
  }, []);

  const applyFilter = (next: FilterState) => {
    setFilter(next);
    const url = `${window.location.pathname}${buildQuery(next)}`;
    window.history.replaceState(null, "", url);
  };

  const visible = useMemo(() => filterFeatures(features, filter), [features, filter]);
  const selected = visible.find((f) => f.properties.site_id === selectedId) ?? null;

  return (
    <div className="app">
      <header className="header">
        <h1>
          築地・明石町 歴史アトラス
          <span className="count">
            {visible.length} / {features.length} 件
          </span>
        </h1>
        <FilterChips state={filter} onChange={applyFilter} />
      </header>
      <main className="main">
        <MapView
          features={visible}
          selectedId={selectedId}
          onSelect={(id) => setSelectedId(id)}
        />
        {selected && (
          <DetailPanel props={selected.properties} onClose={() => setSelectedId(null)} />
        )}
      </main>
      <Attribution />
    </div>
  );
}
