# CLAUDE.md — tsukiji-atlas

@AGENTS.md

Claude Code 固有の補足:
- ループ開始時、`~/.claude/skills/` の loop-observability / worktree-kit スキルの規律が本プロジェクトにも適用される
- ログ・ゲートのスクリプト正本は `harness-kit/` 配下(`harness-kit/loop-observability/scripts/looplog.py` / `harness-kit/worktree-kit/scripts/wtctl.py`)。リポジトリ内 `harness/` は CI 用同梱ミラー(同期方針は harness/README.md)
