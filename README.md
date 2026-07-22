# tsukiji-atlas

築地・明石町の名所旧跡を時代別・分野別に可視化する loop-native プロジェクト。
Wikidata + 東京都オープンデータ + 手動キュレーション → Medallion → MapLibre 地図 → Vercel 公開。

## ドキュメント構成(読む順)

1. **SETUP.md** — 開発開始手順(harness-kit 組み立て → init → 最初のループ)
2. **CLAUDE.md / AGENTS.md** — エージェント規律(共通規律は scaffoldctl init で追記)
3. **SPEC.md** — 要求仕様・ディメンション定義・GeoJSON 契約・品質基準
4. **IMPLEMENTATION_GUIDE.md** — フェーズ計画・各層の設計・並走指定
5. **TEST_SPEC.md** — 要求 ID にトレースするテストケース

## 最初のループ(Claude Code)

```
このリポジトリの CLAUDE.md を読み、7 段階プロトコルに従って
IMPLEMENTATION_GUIDE.md の P1(loop_001)を開始してください。
```
