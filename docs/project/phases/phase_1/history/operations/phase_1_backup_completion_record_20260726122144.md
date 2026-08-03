# Phase 1確定Backup 完了記録

- 文書ID: `phase_1_backup_completion_record`
- 状態: `completed_verified`
- 作成日時: `2026-07-26 12:21:44 JST`
- 更新日時: `2026-07-26 12:21:44 JST`
- Snapshot: `20260726122144`
- Backup Snapshot: `20260726121941`
- 作成担当: 設計者役担当Task
- Backup入力Index: [documentation_index_20260726121346.md](../documentation_index_20260726121346.md)
- Phase 1 Final Review: [designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](../handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)
- Pre-backup Scan: [pre_phase_1_backup_privacy_and_sanitation_scan_20260726121346.md](pre_phase_1_backup_privacy_and_sanitation_scan_20260726121346.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Phase 1確定Backupを作成し、Sanitation、SHA-512、Temporary Restoreおよび保存先Copy後の再検証を完了した。

```text
Backup Status             : COMPLETED／VERIFIED
Phase                     : Phase 1
Milestone                 : portable_runtime_mvp
Backup Snapshot           : 20260726121941
File Count                : 422
Uncompressed File Bytes   : 3,360,052
Archive Size Bytes        : 1,377,193
Restore Verification      : PASS
Privacy Scan              : PASS
Secret Scan               : PASS
```

## 2. Backup Location

Project Root外の次の論理配置へ保存した。

```text
MARGPA-RUNTIME-LLM/
├─ margpa-runtime-llm/
└─ phase_backups/
   └─ phase_1/
```

個人固有Absolute Pathは本書へ記録しない。

## 3. Backup Set

```text
margpa-runtime-llm_phase_1_portable_runtime_mvp_20260726121941.zip
margpa-runtime-llm_phase_1_portable_runtime_mvp_20260726121941_manifest.json
margpa-runtime-llm_phase_1_portable_runtime_mvp_20260726121941_receipt.json
margpa-runtime-llm_phase_1_portable_runtime_mvp_20260726121941_sha512.txt
```

## 4. SHA-512

Archive：

```text
9eaabdee62a36e072df5d990d68e9986ca34b2894f8d6212ac3db4c26c85b2947be6052e0b4bbace2575f774a28eb1694a8e6a846330d6b1c307b75d6931b483
```

Manifest：

```text
e7318bbbc03d24982567ea1f30dbf32ecce41e00885d196a91f8c0b4a82a63f7fb58d1f15b62a63e305988f950d45ed6e75de3f8f1939ba89827113736eebd8c
```

Receipt：

```text
a35e2374f76b436bf993f2011e638458ff03911842b8a5938e7a1180615db962b826d5fc2bc93c922724a204d2b7132e22939c5f383589e2ac67dd6d421ff45a
```

Sidecarの`shasum -a 512 -c`は保存先で3件すべてOKとなった。

## 5. Include Set

```text
.gitignore
.python-version
config/
docs/
pyproject.toml
scripts/
src/
tests/
uv.lock
```

Backup入力時点のCurrent Documentation Index：

```text
docs/documentation_index_20260726121346.md
```

## 6. Excluded Set

```text
.DS_Store
.venv/
Project Root models/
models Symbolic Link
GGUF Model Binary
.git/
.pytest_cache/
.mypy_cache/
.ruff_cache/
__pycache__/
*.pyc
*.pyo
.coverage
htmlcov/
.ipynb_checkpoints/
.env
.env.*
var/
*.log
Local Data
Credential
Secret
```

Model本体は含めず、ManifestへModel ID、File名、QuantizationおよびSHA-512だけを記録した。

## 7. Sanitation Verification

Candidateに対して次を確認した。

```text
Root Directory                    : margpa-runtime-llm/ only
Symbolic Link                     : 0
GGUF                              : 0
.DS_Store                         : 0
.venv                             : 0
Root models                       : 0
Cache／Bytecode                   : 0
Secret File                       : 0
Forbidden Identity Literal        : 0
Private Key／Token Pattern        : 0
```

`config/models/`はModel Registry定義を保持する正規Source Directoryであり、Project RootのModel Artifact置き場`models/`とは異なるためIncludeした。

## 8. Restore Verification

ArchiveをTemporary Directoryへ展開し、次を確認した。

1. Archive Rootが`margpa-runtime-llm/`の1件だけである。
2. Restored File Countが422である。
3. Source CandidateとRestored TreeのRelative Pathが一致する。
4. 全FileのSizeが一致する。
5. 全FileのSHA-512が一致する。
6. Forbidden Artifactが復元されない。
7. Manifest Inventoryと一致する。

結果：

```text
archive_root_valid        : true
inventory_matches_manifest: true
file_hashes_match         : true
restore_completed         : true
restored_file_count       : 422
symlink_absent            : true
forbidden_artifact_absent : true
privacy_scan_passed       : true
secret_scan_passed        : true
```

## 9. Candidate検証の安全停止

最初のTemporary Candidate検証では、禁止対象のProject Root `models/`と、必要な`config/models/`をDirectory名だけで同一視したため、安全側で停止した。

```text
Candidate contains forbidden directory: models
```

このCandidateはArchive確定またはBackup保存していない。

検査条件を次へ修正した。

```text
Forbidden:
  Project Root models/
  Root models Symbolic Link
  GGUF Artifact

Allowed:
  config/models/
```

新Timestamp `20260726121941`でCandidateを作り直し、全検証をPassしたSetだけを確定保存した。

## 10. VCS State

```text
vcs.type   : none
commit     : null
tag        : null
remote     : null
```

Phase 1 BackupはGit開始前Snapshotである。Git初期化またはGitHub公開は行っていない。

## 11. Phase Transition

```text
Phase 1 Backup : COMPLETE
Phase 1-ex     : READY TO START／NOT STARTED
```

初回GitHub公開はPhase 1-ex完了後まで延期する。

## 12. Authorization Boundary

Backup完了はPhase 1-exへ進める状態を示すが、Phase 1-exのSource／Config／Docs Migration、Git操作、Lightning変更またはRAG実装を自動開始しない。
