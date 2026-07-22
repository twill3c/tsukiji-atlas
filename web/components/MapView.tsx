"use client";

// 地図(F-06): MapLibre GL + 地理院タイル(淡色)。60 件規模のためクラスタなし、
// マーカーは時代色 + 白リング(重なり分離)。identity は色単独に依存せず、
// クリックで DetailPanel に時代テキストを表示する
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useEffect, useRef } from "react";

import { eraColor } from "@/lib/dims";
import type { SiteFeature } from "@/lib/types";

const GSI_PALE_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {
    gsi_pale: {
      type: "raster",
      tiles: ["https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution:
        '<a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank">国土地理院</a>',
    },
  },
  layers: [{ id: "gsi_pale", type: "raster", source: "gsi_pale" }],
};

// 初期表示は築地・明石町エリア中心(bbox 中央付近)
const INITIAL_CENTER: [number, number] = [139.7728, 35.666];
const INITIAL_ZOOM = 14.5;

export default function MapView({
  features,
  selectedId,
  onSelect,
}: {
  features: SiteFeature[];
  selectedId: string | null;
  onSelect: (siteId: string) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    mapRef.current = new maplibregl.Map({
      container: containerRef.current,
      style: GSI_PALE_STYLE,
      center: INITIAL_CENTER,
      zoom: INITIAL_ZOOM,
      attributionControl: { compact: false },
    });
    mapRef.current.addControl(new maplibregl.NavigationControl({ showCompass: false }));
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = features.map((f) => {
      const el = document.createElement("button");
      el.className = "marker";
      el.style.background = eraColor(f.properties.era);
      el.dataset.selected = String(f.properties.site_id === selectedId);
      el.setAttribute("aria-label", f.properties.name);
      el.title = f.properties.name;
      el.addEventListener("click", (e) => {
        e.stopPropagation();
        onSelect(f.properties.site_id);
      });
      return new maplibregl.Marker({ element: el })
        .setLngLat(f.geometry.coordinates)
        .addTo(map);
    });
  }, [features, selectedId, onSelect]);

  return <div ref={containerRef} className="map" />;
}
