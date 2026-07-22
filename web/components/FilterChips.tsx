"use client";

// 時代・分野のトグルチップ(F-06)。時代チップは色付きスウォッチを兼ね、
// 地図マーカーの常時凡例として機能する(色単独に依存しないための緩和策)
import { CATEGORIES, ERAS } from "@/lib/dims";
import type { FilterState } from "@/lib/types";

function toggle(values: string[], key: string): string[] {
  return values.includes(key) ? values.filter((v) => v !== key) : [...values, key];
}

export default function FilterChips({
  state,
  onChange,
}: {
  state: FilterState;
  onChange: (next: FilterState) => void;
}) {
  return (
    <div>
      <div className="chips" role="group" aria-label="時代で絞り込み">
        <span className="group-label">時代</span>
        {ERAS.map((era) => (
          <button
            key={era.key}
            type="button"
            className="chip"
            aria-pressed={state.eras.includes(era.key)}
            onClick={() => onChange({ ...state, eras: toggle(state.eras, era.key) })}
          >
            <span className="swatch" style={{ background: era.color }} />
            {era.label}
          </button>
        ))}
      </div>
      <div className="chips" role="group" aria-label="分野で絞り込み">
        <span className="group-label">分野</span>
        {CATEGORIES.map((cat) => (
          <button
            key={cat.key}
            type="button"
            className="chip"
            aria-pressed={state.cats.includes(cat.key)}
            onClick={() => onChange({ ...state, cats: toggle(state.cats, cat.key) })}
          >
            {cat.label}
          </button>
        ))}
      </div>
    </div>
  );
}
