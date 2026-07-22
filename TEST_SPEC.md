# TEST_SPEC.md — tsukiji-atlas

## 実行規約

- `python -m pytest -q --tb=no` を stage 3–5 と wtctl のベースライン/check に使用
- マーカー: `unit` / `integration` / `validation`。全テストはフィクスチャ駆動(N-01、ネットワーク不要)
- フィクスチャ更新は専用コミット(`test: update fixtures`)+ ループログに理由を記録
- 実 Wikidata 疎通は `make bronze` の手動実行のみ(結果はループログに test_run として記録)

## Bronze(T-01x)

| ID | 対応 | ケース | 期待 |
|---|---|---|---|
| T-011 | F-01 | SPARQL 応答フィクスチャの解析 | 共通中間形に変換、座標が float 化される |
| T-012 | F-01/N-02 | タイムアウト応答のモック | リトライ 3 回後に DATA-SRC 相当の例外、部分結果を残さない |
| T-013 | F-02 | 都 OD CSV フィクスチャ | 中央区行のみ抽出、想定列の存在検証(列欠落は失敗) |
| T-014 | F-03 | curated CSV 読込 | verified=false が仕分けされ件数が返る |
| T-015 | F-03 | curated の必須列欠落 | 明示的エラー(黙って欠損行スキップしない) |

## Silver(T-02x)

| ID | 対応 | ケース | 期待 |
|---|---|---|---|
| T-021 | F-04 | qid 指定ありの名寄せ | curated と wikidata が 1 レコードに統合、座標は curated 優先 |
| T-022 | F-04 | qid 指定なし・同名 | 統合されない(別レコードのまま) |
| T-023 | F-04 | era 機械判定 | P571=1869 → meiji、1657 → edo_early、境界年(1868)→ meiji |
| T-024 | F-04 | era 判定不能 | needs_review に出力され Silver 本体から除外されない(era=null で保持) |
| T-025 | F-04 | NFKC 正規化 | 全角英数・互換文字が正規化された name_norm を持つ |

## Gold(T-03x)

| ID | 対応 | ケース | 期待 |
|---|---|---|---|
| T-031 | F-05/Q-03 | GeoJSON 契約 | 必須 properties 充足、era/category が定義キーのみ |
| T-032 | Q-02 | bbox 検証 | 域外座標が validate で FAIL(bbox は config/areas から読む) |
| T-033 | Q-04 | site_id/qid 一意性 | 重複注入フィクスチャで FAIL |
| T-034 | Q-05 | verified=false 除外 | Gold に含まれず counts.json の excluded に計上 |
| T-035 | Q-01 | 件数下限 | 39 件フィクスチャで FAIL、40 件で PASS |
| T-036 | F-05 | 独立再計算(三角測量) | counts.json の時代別合計 = 総件数 = GeoJSON Feature 数を別経路で再計算し一致 |

## Web(T-04x)— P4 で詳細化

| ID | 対応 | ケース | 期待 |
|---|---|---|---|
| T-041 | F-06 | フィルタロジック(純関数として切り出す) | era/category の AND-of-OR 絞り込みが正しい |
| T-042 | F-06 | URL クエリ ↔ 状態の相互変換 | 往復で不変(roundtrip) |
| T-043 | F-07 | 詳細パネルのデータ整形 | year 欠落時の表示、license 表記の分岐 |

## 手動確認(自動化対象外)

- Q-06: summary の逐語一致なし(公開前に全件目視。チェック結果をループログに記録)
- 地図の実表示・地理院タイル帰属・色覚配慮(P4 完了時チェックリスト)
- Vercel 本番 URL の疎通と Lighthouse 簡易確認(P5)
