"use client";

// F-07: 名称・時代・分野・year・summary・source・license を表示
import { eraColor } from "@/lib/dims";
import { formatDetail } from "@/lib/format";
import type { SiteProps } from "@/lib/types";

export default function DetailPanel({
  props,
  onClose,
}: {
  props: SiteProps;
  onClose: () => void;
}) {
  const d = formatDetail(props);
  return (
    <aside className="panel" aria-label={`${d.name} の詳細`}>
      <button type="button" className="close" onClick={onClose} aria-label="閉じる">
        ×
      </button>
      <h2>{d.name}</h2>
      <p className="summary">{d.summary}</p>
      <dl>
        <dt>時代</dt>
        <dd>
          <span className="era-tag">
            <span className="swatch" style={{ background: eraColor(props.era), width: 10, height: 10, borderRadius: "50%", display: "inline-block" }} />
            {d.eraLabel}({d.yearText})
          </span>
        </dd>
        <dt>分野</dt>
        <dd>{d.categoryLabel}</dd>
        <dt>出典</dt>
        <dd>
          {d.sourceLabel}
          {d.qid && (
            <>
              {" · "}
              <a href={`https://www.wikidata.org/wiki/${d.qid}`} target="_blank" rel="noreferrer">
                {d.qid}
              </a>
            </>
          )}
        </dd>
        <dt>権利</dt>
        <dd>{d.licenseText}</dd>
      </dl>
    </aside>
  );
}
