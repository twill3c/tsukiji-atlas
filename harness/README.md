# harness/ — CI 用同梱ミラー

**正本は `../harness-kit/`(ローカル、GitHub には置かない方針)。ここは CI が使う読み取り専用ミラー。**

| ファイル | 正本 |
|---|---|
| `scripts/looplog.py` | `harness-kit/loop-observability/scripts/looplog.py` |
| `scripts/wtctl.py` | `harness-kit/worktree-kit/scripts/wtctl.py` |
| `schema/taxonomy.json` | `harness-kit/loop-observability/schema/taxonomy.json` |

- ここを直接編集しない。harness-kit 側を更新 → コピーし直す(`chore:` 専用コミット)
- ドリフト検査: `diff -r harness/scripts ../harness-kit/.../scripts` が非空なら同期漏れ
- ローカルのループ運用は従来どおり harness-kit 側を直接使ってよい(同一内容)
