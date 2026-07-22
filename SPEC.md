# SPEC.md — tsukiji-atlas

## 1. 目的

築地・明石町エリア(将来: 中央区全域)の名所旧跡・文化財・記念碑を、公開情報から
再現可能なパイプラインで収集し、時代別・分野別にフィルタできる Web 地図として公開する。
併せて、harness-kit 3 モジュール(ログ・スキャフォールド・worktree)の初回実地検証を行う。

## 2. スコープ

- 初期エリア: `tsukiji-akashicho`。bbox は緯度 35.658–35.674 / 経度 139.764–139.786(仮置き。loop_001 で確定)
- 初期目標件数: 40–60 件(curated の際限ない追加を抑制する上限としても機能させる)
- スコープ外: 飲食店・現役商業施設の網羅、写真の収集・掲載、多言語対応(P6 以降で検討)

## 3. 機能要求

| ID | 要求 | 優先度 |
|---|---|---|
| F-01 | Wikidata SPARQL から中央区の史跡・文化財・記念碑を座標付きで抽出できる(Bronze) | must |
| F-02 | 東京都オープンデータの文化財一覧 CSV を取得・正規化できる(Bronze) | must |
| F-03 | 手動キュレーション CSV(data/curated/sites.csv)を Bronze の一系統として取り込める | must |
| F-04 | 3 系統を名寄せし、時代・分野ディメンションを付与した Silver を生成できる | must |
| F-05 | Gold として sites.geojson(§5 契約)と品質レポート(counts.json)を生成できる | must |
| F-06 | 地図 UI: 全件表示、時代フィルタ(複数選択)、分野フィルタ、ピン選択で詳細パネル | must |
| F-07 | 詳細パネルに名称・時代・分野・year・summary・source・license を表示する | must |
| F-08 | 静的エクスポートで Vercel に公開できる(環境変数・サーバ不要) | must |
| F-09 | GitHub Actions 月次 cron でパイプラインを再実行し、差分があれば PR を作成する | should |
| F-10 | エリアキーによる P6 拡張(日本橋・佃/月島)がコード変更なし・設定追加のみで可能 | should |

## 4. ディメンション定義

### dim_時代(era)— 7 区分

| key | 表示名 | 目安 | 代表例 |
|---|---|---|---|
| edo_early | 江戸前期 | 1603–1700 | 明暦大火後の埋立、築地本願寺移転 |
| edo_late | 江戸後期 | 1701–1852 | 浅野内匠頭邸跡ほか武家地 |
| bakumatsu | 幕末 | 1853–1867 | 軍艦操練所、蘭学塾(慶應義塾発祥) |
| meiji | 明治 | 1868–1911 | 築地居留地、教会・ミッションスクール、電信創業 |
| taisho | 大正 | 1912–1925 | 関東大震災関連 |
| showa | 昭和 | 1926–1988 | 築地市場開場(1935)、勝鬨橋 |
| heisei_reiwa | 平成以降 | 1989– | 市場移転(2018)関連 |

判定は「その地物・出来事が主として帰属する時代」1 つ。複数時代にまたがる場合は
成立・創建時点を採る(era 列)。年が判明する場合は `year` に西暦を併記する。

### dim_分野(category)— 8 区分

`shrine_temple_church`(寺社・教会)/ `samurai_site`(武家地・屋敷跡)/
`monument_origin`(発祥の地・記念碑)/ `edu_medical`(教育・医療)/
`naval_military`(軍事・海軍)/ `market_food`(市場・食文化)/
`bridge_civil`(橋梁・土木)/ `literature_arts`(文学・芸能)

## 5. Gold 契約: sites.geojson

FeatureCollection。各 Feature の properties:

| 列 | 型 | 必須 | 備考 |
|---|---|---|---|
| site_id | string | ✓ | `{area}-{連番3桁}` |
| name | string | ✓ | |
| era | string | ✓ | §4 の key |
| category | string | ✓ | §4 の key |
| year | int | – | 西暦。不明なら省略 |
| summary | string | ✓ | 自前執筆 120 字以内 |
| source | string | ✓ | `wikidata` / `tokyo_od` / `curated` |
| qid | string | – | Wikidata QID(判明時) |
| license | string | ✓ | `CC0` / `CC BY 4.0` / `self` |
| area | string | ✓ | エリアキー |

geometry は Point(経度・緯度)。

## 6. 品質基準(→ TEST_SPEC にトレース)

| ID | 基準 |
|---|---|
| Q-01 | Gold 件数: エリア初期リリース時 40 件以上 |
| Q-02 | 全 Feature の座標がエリア bbox 内(検証は config/areas から bbox を読む) |
| Q-03 | era / category / source / license の充足率 100%、値は定義済みキーのみ |
| Q-04 | site_id 一意、qid の重複なし(名寄せ後の二重登録検出) |
| Q-05 | curated の verified=false は Gold に含まれない。除外件数を counts.json に記録 |
| Q-06 | summary は 120 字以内、外部サイト本文との逐語一致なし(目視 + 手動チェックリスト) |

## 7. 非機能要求

| ID | 要求 |
|---|---|
| N-01 | パイプラインはネットワークなしでフィクスチャから全層再現可能(テスト用) |
| N-02 | 実 Wikidata へのクエリはリトライ・タイムアウト・スリープを備える(DATA-SRC 対策) |
| N-03 | 地図初期表示 3 秒以内(静的 GeoJSON 1 ファイル、60 件規模なら自明に満たす) |
| N-04 | 出典表示: 地理院タイル・CC BY データの表示画面に帰属を明示 |
