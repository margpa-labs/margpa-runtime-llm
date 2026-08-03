# 公開前プライバシーScrub実施記録

- 文書ID: `publication_privacy_scrub_report`
- 状態: `complete`
- 作成日時: `2026-07-20 22:02:16 JST`
- 更新日時: `2026-07-20 22:02:16 JST`
- Snapshot: `20260720220216`
- 実施担当: 設計者役担当Task
- 正本言語: 日本語
- Policy: [public_identity_and_personal_information_policy_20260720220216.md](../requirements/public_identity_and_personal_information_policy_20260720220216.md)
- supersedes: なし

## 1. 目的

Phase 1公開準備に先立ち、Project管理対象Fileから第一者の非公開IdentityとLocal環境情報を除去し、公開Identityを`Nazuna Research`へ統一する。

## 2. 対象

Project Root以下の管理候補Fileを再帰走査した。次は公開対象外または第三者管理物のため本文置換対象から除外した。

- `.venv/`
- `models` Symlinkの参照先とModel本体
- `.git/`
- Tool Cache、Bytecode、Coverage Data

Symlinkを辿る走査は行わず、外部Model Storageを変更していない。

## 3. 実施内容

- 第一者の旧Identity表記を`Nazuna Research`へ統一
- 内部通称を`Nazuna Research Governance LLM`へ統一
- 個人固有のProject Root、Definition Source、Model Rootを抽象Pathへ置換
- Local Temporary Pathを再現不能なPlaceholderへ置換
- 旧Handle表記揺れを`Nazuna Research`へ統一
- `.DS_Store`、Coverage Data、Project内Cache／Bytecodeを除去
- File名についても旧Identity表記を走査
- Email、連絡先、Private Key、SecretらしきPatternを走査

## 4. 最終結果

管理対象File内に、第一者の旧Identity、Local Account名、個人固有Project Path、個人Email、Private Keyの残存を認めなかった。

次は意図的に保持した。

- `example`を用いた架空のAbsolute Path: Privacy RedactionのUnit Test Data
- `/Users/...`という抽象表現: User固有Absolute Pathを禁止する設計例
- Model／Library／Repository／Licenseの第三者正式名称
- `Nazuna Research`

## 5. Local-only境界

`.venv/`と`models` SymlinkはLocal実行のため現存するが、`.gitignore`および公開方針で公開対象外である。公開Archive作成時は、これらが収録されていないことをManifestで再確認する。

Filesystem Owner等のOS MetadataはRepository本文ではない。Archive作成ToolがOwner Metadataを保存する場合は、公開用Archive生成時に正規化する。

## 6. 履歴への影響

Privacy／Security例外により、個人情報を含んでいた既存Docsは匿名化された。したがって、一部の過去Snapshotは作成当時のBit列と一致しない。

これは意図的な安全上の変更であり、削除した値を履歴復元のために再記録しない。文書上のDecision、Phase状態、設計内容は保持した。

## 7. 再実施条件

次の時点で再走査する。

- Git初期化前
- GitHub Push前
- Source Archive／Backup作成前
- README／Public Docs完成後
- Screenshot、Sample Log、Evidence追加後
- 外部環境で生成したLogの取り込み前
