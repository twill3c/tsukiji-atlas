# データライセンス(LICENSE-DATA)

本リポジトリの**コード**は MIT License(リポジトリ直下の `LICENSE`)、
**データ**は本ファイルの宣言に従う(SPEC N-05 の二層構成)。

## 系統別ライセンス

| 系統 | 対象 | ライセンス | 帰属 |
|---|---|---|---|
| curated | `data/curated/sites.csv`(summary 含む全列。summary は自著) | CC BY 4.0 | Tetsuro Sakata (twill3c) / tsukiji-atlas |
| Wikidata 由来 | QID・座標・クラス・指定区分等の事実データ | CC0 1.0 | 帰属不要(Wikidata) |
| 東京都オープンデータ由来 | 文化財一覧 CSV の事実データ(名称・座標・分類・指定日) | CC BY 4.0 | 東京都教育委員会 |

## 生成物(sites.geojson / counts.json)

`web/public/data/sites.geojson` と `counts.json` は上記 3 系統の混合著作物であり、
**全体として CC BY 4.0** で提供する。帰属は本ファイルおよび公開サイトの
Attribution 欄(地理院タイル・東京都オープンデータ CC BY 4.0・Wikidata CC0・
自前調査 CC BY 4.0)の表記に従う。

## 注記

- 区・寺社等の Web ページの解説文は転載していない(summary は全件自前執筆、AGENTS §2)
- 地図タイルは国土地理院(出典表示必須)。データ本体には含まれない
