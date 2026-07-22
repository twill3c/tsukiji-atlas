# AGENTS.md — tsukiji-atlas

築地・明石町を起点に、中央区の名所旧跡を時代別・分野別に可視化する loop-native プロジェクト。
Wikidata SPARQL + 都オープンデータ + 手動キュレーション CSV を Medallion で整備し、
MapLibre 地図として Vercel に公開する。

読む順: 本書 → SPEC.md → IMPLEMENTATION_GUIDE.md(該当フェーズ)→ TEST_SPEC.md。

---

## プロジェクト固有規律

### 1. エリア抽象化(最重要)

すべての抽出・変換・UI 表示は、エリアキー(`tsukiji-akashicho` / 将来 `nihonbashi` /
`tsukuda-tsukishima`)を引数に取る関数・設定経由で行う。エリア固有の値
(bbox・地名・シード CSV パス)を transform / UI にハードコードしてはならない。
設定は `config/areas/{area}.json` に集約する。
理由: P6 のエリア拡張(brownfield)を成立させる前提条件。

### 2. 出典と権利の規律

- 全レコードは `source`(wikidata / tokyo_od / curated)と `license` 列を必須とする
- 都オープンデータ由来のデータを表示する画面には CC BY の出典表示を置く。地理院タイルは出典表示必須
- **区・寺社等の Web ページの解説文を転載しない**。summary はすべて自前で書く(事実情報
  — 名称・所在地・年代・指定区分 — のみ利用可)。Wikidata は CC0
- 迷ったら escalation。権利まわりの推測実装は禁止

### 3. データの真実性

- curated CSV の座標は `verified` 列(true/false)で管理する。false の座標を Gold に
  流してはならない(Silver で除外し、件数を品質レポートに出す)
- 名寄せ(curated ↔ Wikidata)は `qid` 列の明示指定のみで行う。名称の曖昧一致で
  自動統合しない(同名別地物が多い土地柄)
- 存在が確認できない史跡を「それらしく」生成しない。1 件の捏造は全件の信頼を壊す

### 4. 技術スタック規約

- パイプライン: Python 3.12 標準ライブラリ + requests のみ(pandas 不使用。件数規模的に不要)
- Web: Next.js(App Router)+ MapLibre GL JS + 地理院タイル。静的エクスポート(`output: 'export'`)
- データ受け渡しは `public/data/sites.geojson` の 1 ファイル契約(スキーマは SPEC §5)
- テスト: pytest、全テストはフィクスチャ駆動(ネットワーク不要)。実 Wikidata への疎通は
  `make bronze` の手動実行のみ

### 5. ループ運用

- 1 ループ 1 フェーズ内タスク。P2(Silver)と P4(地図 UI)は要求 ID が独立しており
  worktree 並走可。それ以外の並走は事前にエスカレーション
- SPARQL の実データ確認(loop_001)までは SPEC の該当箇所は「仮置き」であり、
  確認結果による SPEC 更新は SPEC-DRIFT ではなく正規の手順(専用コミット)

<!-- scaffoldctl init 実行後、この下に managed block(共通規律・ログ義務・worktree 規律)が追記される -->

<!-- scaffold:block agents_core v1.0.0 -->
## 共通規律(scaffold 管理領域 — 手動編集禁止)

このセクションはスキャフォールド・レジストリが管理する。内容を変更したい場合は、
このファイルを直接編集せず、失敗ログ → HARNESS_CHANGELOG 起票 → レジストリ改訂 → `scaffoldctl update` の経路で行うこと。

### 7 段階ループプロトコル

| 段階 | 名称 | 完了条件 |
|---|---|---|
| 1 | 計画 | 対象の要求 ID を特定し、`loop_start` を記録した |
| 2 | 文脈読込 | SPEC.md / IMPLEMENTATION_GUIDE.md の該当箇所と、直近ループのログを読んだ |
| 3 | テスト先行 | TEST_SPEC.md にトレースする失敗するテストを書き、赤を確認した |
| 4 | 実装 | ファイル編集 2 回ごとにテストを実行し、赤のまま次の編集に進んでいない |
| 5 | 検証 | 全テスト合格 + 独立再計算(該当時)を確認した |
| 6 | 文書同期 | SPEC/docs と実装の乖離(SPEC-DRIFT)を解消し、生成ドキュメントを再生成した |
| 7 | 完了 | `loop_end` を記録し、ループログ validate に合格し、専用コミットを積んだ |

### ループ可観測性

全ループは loop-observability の規律(LOOP_LOG_SPEC / FAILURE_TAXONOMY)に従い
`logs/loops/{loop_id}.jsonl` に記録する。失敗は気づいた瞬間に分類コード付きで記録する。
ツーストライク(LL-10)と S1 即時起票(LL-12)は本プロジェクトでも有効である。

### エスカレーション規範

以下の場合は作業を止め、`escalation` を記録してから人間に確認する:
仕様の複数解釈(SPEC-AMB 相当)/ スコープ外ファイルへの変更が必要になった /
破壊的操作(履歴改変・データ削除・強制 push)/ 同種の修正の 3 回目の失敗(PROC-LOOP)。

### コミット規約

Conventional Commits(feat/fix/test/docs/refactor/chore)。スキャフォールド更新は
`chore: scaffold vX.Y.Z` の専用コミットで行い、機能変更と混ぜない。
<!-- /scaffold:block agents_core -->
