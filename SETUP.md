# SETUP.md — 開発開始手順(VS Code + Claude Code)

所要 30 分程度。一度きりの手順(1〜3)と、本プロジェクトの初期化(4〜6)。

## 1. harness-kit の組み立て(未実施の場合のみ)

```bash
cd ~/dev
mkdir harness-kit && cd harness-kit
# 3 つの zip(loop-observability / scaffold-kit / worktree-kit)をここに展開
unzip ~/Downloads/loop-observability-v1.0.zip
unzip ~/Downloads/scaffold-kit-v1.0.zip
unzip ~/Downloads/worktree-kit-v1.0.zip
cp scaffold-kit/templates/HARNESS_CHANGELOG.md ./HARNESS_CHANGELOG.md   # HC 台帳は中央に一本化
git init -b main && git add -A && git commit -m "chore: harness-kit v1.0"
# (GitHub twill3c/harness-kit に push)
```

## 2. install.json の配線(レジストリに (1)(3) を登録)

`scaffold-kit/registry/install.json` の components に以下を追記する:

```json
{"type": "file", "id": "looplog",  "source": "../../loop-observability/scripts/looplog.py", "target": "harness/looplog.py"},
{"type": "file", "id": "taxonomy", "source": "../../loop-observability/schema/taxonomy.json", "target": "harness/taxonomy.json"},
{"type": "file", "id": "wtctl",    "source": "../../worktree-kit/scripts/wtctl.py", "target": "harness/wtctl.py"},
{"type": "file", "id": "wtgate",   "source": "../../worktree-kit/config/gate.example.json", "target": ".wt/gate.json"}
```

さらに (1)(3) の AGENTS_SNIPPET 本文を `registry/blocks/loop_observability.md` /
`registry/blocks/worktree_discipline.md` として保存し、block としても登録する
(スクリプトパスは `harness/looplog.py` / `harness/wtctl.py` に読み替えて保存すること)。
配線後: `VERSION` を 1.1.0、CHANGELOG に追記、コミット。

※ 本プロジェクトには `.wt/gate.json` を先行同梱している(免除パスに `public/data/*` を追加済み)。
init 時に「既に存在(上書きしません)」と出るのは正常。

## 3. Claude Code スキルの配置

```bash
mkdir -p ~/.claude/skills
cp -r ~/dev/harness-kit/loop-observability ~/.claude/skills/
cp -r ~/dev/harness-kit/worktree-kit ~/.claude/skills/
cp -r ~/dev/harness-kit/scaffold-kit ~/.claude/skills/
```

## 4. 本プロジェクトの初期化

```bash
cd ~/dev
# この tsukiji-atlas フォルダを配置してから:
cd tsukiji-atlas
git init -b main
python ../harness-kit/scaffold-kit/scripts/scaffoldctl.py init \
  --registry ../harness-kit/scaffold-kit/registry
git add -A && git commit -m "chore: scaffold v1.1.0 — tsukiji-atlas 初期化"
# (GitHub twill3c/tsukiji-atlas を作成して push)
```

init 後、AGENTS.md の末尾に managed block(共通規律・ログ義務・worktree 規律)が
追記され、`harness/` に looplog.py / wtctl.py が入っていることを確認する。

## 5. VS Code で開く

```bash
code ~/dev/tsukiji-atlas
```

- 統合ターミナルで `claude` を起動(Claude Code 拡張でも可)
- worktree 並走時は `wtctl open` 後に `code ../tsukiji-atlas.worktrees/loop_xxx` で
  **別ウィンドウ**として開く(1 ウィンドウ 1 worktree 1 エージェント)

## 6. 最初のループの始め方(Claude Code に貼るプロンプト)

```
このリポジトリの CLAUDE.md を読み、7 段階プロトコルに従って
IMPLEMENTATION_GUIDE.md の P1(loop_001)を開始してください。
loop_001 の目的は Wikidata の実データ確認と QID の確定であり、
SPEC の凍結はその結果を見てから行います。
```

## 7. Vercel(P5 で使用)

- https://vercel.com で GitHub 連携 → tsukiji-atlas を Import(P5 到達時)
- Framework: Next.js / 静的エクスポート。環境変数は不要(全データ静的)
