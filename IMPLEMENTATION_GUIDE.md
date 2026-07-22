# IMPLEMENTATION_GUIDE.md — tsukiji-atlas

## 0. ディレクトリ計画

```
tsukiji-atlas/
├── config/areas/tsukiji-akashicho.json   # bbox・表示名・シードCSVパス
├── extract/          # Bronze: wikidata.py / tokyo_od.py / curated.py + queries/*.rq
├── transform/        # Silver: normalize.py / merge.py / dims.py
├── gold/             # export_geojson.py / validate.py
├── data/
│   ├── curated/sites.csv        # 手動キュレーション(Git管理)
│   ├── bronze/                  # 生取得物(gitignore、fixtures が正)
│   └── fixtures/                # テスト用固定データ(Git管理)
├── public/data/sites.geojson    # Gold 出力(生成物、ゲート免除)
├── web/              # Next.js(app/ components/)※ルート直下でも可、P4 で確定
├── tests/
└── harness/          # scaffoldctl init が配置(looplog.py / wtctl.py / taxonomy.json)
```

## 1. フェーズ計画

| フェーズ | ループ | 内容 | 完了条件 |
|---|---|---|---|
| P1 | loop_001 | **実データ探査**: 中央区の QID・使えるプロパティ・ヒット件数を小さな SPARQL で確認。都 OD の文化財 CSV の列構成確認。結果をもとに SPEC §2 bbox・§3 を確定(専用コミット) | 探査メモ + SPEC 確定 |
| P1 | loop_002 | Bronze 3 系統実装(F-01〜03)+ フィクスチャ作成 | T-01x 合格 |
| P2 | loop_003 | Silver: 正規化・名寄せ・ディメンション付与(F-04) | T-02x 合格 |
| P3 | loop_004 | Gold: geojson 出力 + validate(F-05, Q-01〜05) | T-03x 合格 |
| P4 | loop_005 | 地図 UI(F-06〜07)。**loop_004 と worktree 並走可** | T-04x + 手動確認 |
| P5 | loop_006 | Vercel 公開(F-08)+ 月次 cron(F-09)+ ライセンス配置(N-05) | 本番 URL 疎通 + LICENSE 配置済み |
| P6 | loop_007+ | エリア拡張: 日本橋 → 佃・月島(F-10、brownfield) | 設定追加のみで成立 |

並走規律: P3(loop_004)と P4(loop_005)は `public/data/sites.geojson` の契約(SPEC §5)を
境界として独立。P4 はフィクスチャ GeoJSON で開発し、実データ結線は P5 冒頭で行う。

## 2. Bronze 設計

### 2.1 Wikidata(extract/wikidata.py + queries/*.rq)

- shiro-lens の教訓を踏襲: **OPTIONAL だらけの単一巨大クエリを避け、小さく分割**して
  Silver で結合する。`sites_base.rq`(座標+区)/`sites_heritage.rq`(指定区分)/
  `sites_dates.rq`(成立年)の 3 本を基本形とする
- **loop_001 確認結果**(詳細は docs/loop_001_exploration.md): 中央区 = **Q212704**。
  P131 は町丁粒度(築地 Q1201337・明石町 Q11512542 等)が多く、**`wdt:P131+` を使用**
  (直付け 284 件 / 推移的 535 件、P625 充足 56% / 66%)。記念碑系クラス
  (Q4989906 / Q5003624 / Q839954 / Q1081138)は **0 件** — ヒットは神社 23・橋 25・
  仏教寺院 8・教会堂 1(P31/P279* ルート別)。P1435 は重文 13・国宝 6 ほかで有効 →
  sites_heritage.rq の設計は維持。記念碑・跡地系は curated が主源泉となる
- リトライ 3 回・タイムアウト 60s・リクエスト間 2s スリープ、User-Agent 明示(N-02)。
  タイムアウトは DATA-SRC としてログに記録する

### 2.2 東京都オープンデータ(extract/tokyo_od.py)

- 文化財一覧 CSV を取得し、所在地に「中央区」を含む行へフィルタ。列名は取得時点の
  実物で確認し fixtures に固定(列構成変更は DATA-SRC)
- **loop_001 確認結果**: `130001_cultural_property.csv`(推奨データセット準拠、cp932、36 列)に
  **緯度・経度列あり → ジオコーディング不要**。中央区該当は現状 1 件(一石橋迷子しらせ石標、
  八重洲 = bbox 外)のみ。tsukiji-akashicho では 0 件でも正常とし、汎用実装で日本橋拡張に備える

### 2.3 curated(extract/curated.py)

- `data/curated/sites.csv` を読み、`verified` で仕分け(Q-05)。スキーマは同 CSV のヘッダが正
- 座標の検証手順: 地理院地図で目視確認 → verified=true に更新(このコミットは
  `data: verify coordinates` の専用コミットとする)

## 3. Silver 設計(transform/)

- 正規化: 全系統を共通中間形(dict のリスト)へ。文字正規化は NFKC、名称の異体字は
  そのまま保持(name_norm 列を別途持つ)
- 名寄せ: `curated.qid` が指定されている場合のみ Wikidata レコードと統合(AGENTS §3)。
  統合時の優先順位: 座標 = curated(verified) > wikidata、summary = curated、指定区分 = tokyo_od/wikidata
- ディメンション: era は curated では手入力、wikidata 由来は P571(成立年)から §4 の
  年代範囲で機械判定し、判定不能は `needs_review.csv` に出して curated 側で確定する

## 4. Gold 設計(gold/)

- export_geojson.py: SPEC §5 契約の FeatureCollection を `public/data/sites.geojson` へ
- validate.py: Q-01〜Q-05 を機械検査。**validate 合格を loop_004 の完了条件に含める**。
  counts.json に件数・時代別・分野別・除外件数を出力(地図 UI のサマリ表示にも使用)

## 5. Web 設計(P4)

- Next.js App Router、`output: 'export'`。MapLibre GL JS + 地理院タイル(淡色)
- 状態は URL クエリに持つ(`?era=meiji,bakumatsu&cat=monument_origin`)— 共有可能な絞り込み
- コンポーネント: `Map`(ピン+クラスタなし、60 件想定)/ `FilterChips` / `DetailPanel` / `Attribution`
- 帰属表示(N-04): 地理院タイル・東京都オープンデータ(CC BY)・Wikidata(CC0)を Attribution に常時表示
- スタイル方針は frontend-design スキル参照。時代別の色は 7 色のカテゴリカルパレット、
  色覚多様性に配慮(P4 で確定)

## 6. CI / cron(P5)

- loop-verify: pytest → `harness/looplog.py validate` → `harness/wtctl.py gate --base origin/main`
- 月次 cron: `make bronze && make silver && make gold` → `public/data/` に差分があれば
  `data: monthly refresh` の PR を自動作成(差分ゲートは免除パスにより通過する)

## 6.5 ライセンス配置(loop_006 内・public 化の前提条件)

public 化はライセンス配置の完了後に行う。順序を逆にしない。

1. リポジトリ直下に `LICENSE`(MIT、著作権者表記は Tetsuro / twill3c)を配置する
2. `data/curated/LICENSE-DATA.md` を作成し、データ層のライセンスを宣言する:
   curated 由来(summary 含む)= CC BY 4.0、Wikidata 由来 = CC0、
   東京都オープンデータ由来 = CC BY 4.0(東京都教育委員会)。
   sites.geojson は混合著作物として全体 CC BY 4.0、帰属は本ファイルと
   サイトの Attribution 欄に従う旨を明記する
3. README.md に「ライセンス」節を追加し、コード = MIT / データ = CC BY 4.0 の
   二層構成と LICENSE-DATA.md への参照を書く(既存の「ライセンス: 未定」を置換)
4. Web の Attribution コンポーネント(N-04)の表記と LICENSE-DATA.md の内容が
   一致していることを確認する
5. public 化の直前に、Git 全履歴に秘匿情報がないことを確認する
   (`git log -p | grep` での目視に加え、wtctl gate の秘密情報スキャンを
   初回コミットからの全差分に対して実行: `python harness/wtctl.py gate --base <初回コミットSHA>`)

注: harness-kit リポジトリの public 化はスコープ外(独立の判断。当面 private)。

## 7. エスカレーション対象(既知の判断待ち)

- ~~中央区 QID と記念碑系クラスの実態~~(**解消済み** loop_001: Q212704 / 記念碑系クラス 0 件、curated 主源泉)
- ~~都 OD CSV の座標有無 → ジオコーディング方針~~(**解消済み** loop_001: 座標列あり、ジオコーディング不要)
- web/ をルート直下に置くかサブディレクトリにするか(Vercel の設定都合、loop_005 冒頭で決定)
