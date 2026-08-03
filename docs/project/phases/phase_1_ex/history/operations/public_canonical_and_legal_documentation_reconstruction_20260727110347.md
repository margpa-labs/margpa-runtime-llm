# Public／Canonical／Legal Documentation Reconstruction Record

```yaml
document_id: public_canonical_and_legal_documentation_reconstruction
status: completed_with_known_pre_initial_commit_review
phase: phase_1_ex
created_at: 2026-07-27 11:03:47 JST
owner: 設計統括者役
git_operation: none
external_operation: none
```

## 1. 目的

Source Inventory、Current Canonical、Phase 1／Phase 1-ex Lossless、Sharedおよび第1周Project Continuity／RoadmapをSourceとして、GitHub上で人が読める日本語Public Corpus、Root README、Research Preview利用条件および引用情報を構築した。

Project Continuity MasterとRoadmapは、ユーザー指示どおり再構築の最初と最後に二周した。

## 2. 作成・更新Artifact

| Artifact | Lines | SHA-512 |
|---|---:|---|
| `README.md` | 236 | `0c1077021cd5930d9ba956da80c0060281ef1b0ce649e678b946643d0ee744fdb9ed324e6dca2e7c9f1b4b488717ceac01add37759b629d40d0dd698909b7c5f` |
| `LICENSE` | 110 | `8d378c4c2994c3e55bb2ccaae27367eb7e66c5da04d028a0d73d727a330ab1ebf0d71f98c9d4f667f2fe6c43881f50d2e5d1fab74b5fd908e357a3db6e867485` |
| `TERMS_OF_USE.md` | 124 | `83ee862ca210f03e50c32a289f4d45f36335678adb377a0bfaac25a0b108d7eb52f1ec5f028a8f8167239f440992fe4e3e9771b244cde492f0cd19d2a4f3c1da` |
| `NOTICE.md` | 108 | `8ae8440b7fea8c10663608deee3b352fc960a25fb8f4197518dd6ceb9c60179011b1bbaefc8756fe9add0714020d50fcdd929615c91eb7913882076e027af0c3` |
| `CITATION.cff` | 34 | `9260fd358f8821df72a28c022b30630f948c91ae7611d132f7a777d343a0aade8ce2b3714773122267f173521b6a5968c397fa5643a07676a80278be2a5f86d1` |
| `docs/public/overview_ja.md` | 23 | `5866fceee5f43775d880b64fc6f0956c23efde8e81f6ba2f8b7774ba11d90a171e381d5706e01e29bc05dde932943c97c1563e34dc7964fbd81fa10e3957bf71` |
| `docs/public/concept_ja.md` | 140 | `7ac64ccaa77c3dcce6bcda6b7c04f0af0b94759632051bf8cf0054e4e70ba38c1dfff602ddb1717187b8af32066448ccfa87e2027f3fd55d4f1b4948c5cb21d6` |
| `docs/public/roadmap_ja.md` | 1716 | `0a3fbaac2cf247f0999213d3c8866a5537b8112a656dee7b9588c92c76a6a3b892799da938c6415fe8bffff9fd378b4726f0f79cd01bd4ed71c8434796f88e02` |
| `docs/project/current/project_continuity/project_continuity_master_ja.md` | 1025 | `7c6c1faba5f1adc2f1f8a9429ffd4e35cd7a6df4e233bb6b793025c0131e5a8c19c0775957778a493d3e8b5c1f26a369246340f05a35c76ec0e026b14a69a740` |
| `docs/project/current/documentation_index_ja.md` | 179 | `a9708edb1a5069d76ef6754ac21b28e8153ef85c128d88a7d936273d0897f778d6dd176211becdde54f516fc23b5fac85446168c78aaab2c7e19463e1c81a77f` |

## 3. Public内容

README：

- Roadmapを最初に読む導線を強調した。
- Demo画像6枚を相対Pathで掲載した。
- Phase状態と実装済み範囲を示した。
- 現行Qwen3-4BはHardware制約下のBaselineであり、最終性能Targetではないことを示した。
- macOSの技術参照用Setupを記載した。
- 匿名Public Demo、Traffic-aware Wake-upおよびGitHub公開が未完了であることを示した。
- Research Preview、非OSS、無保証および高Risk用途禁止を示した。
- 末尾に英語Abstractを付けた。

Concept：

- Model外側のRuntime Governanceを中心に据えた。
- Model／Backend／Config／GD／Guardrail／Judge／Repair／RAG／Agent／Storage／UI／Deploymentの疎結合を示した。
- 共有Governance Control Plane＋分散Governance Pointを示した。
- Definition 0件、未知Definition、GD名非Hard-codeを示した。
- `off／observe／enforce`と依存関係検証を示した。
- EASA、DLAGSA、OCILNSの公開可能な名称、研究領域、概要および接続方向を示した。

利用条件：

- Repositoryは閲覧・非公開評価だけを許可するResearch Previewである。
- 公式Hosted Demoは公開時のUIと制限内で操作できる。
- Hosted Demo操作許可はRepository成果物の複製・改変・実行・配布・商用利用を許可しない。
- 動作、互換性、正確性、安全性、可用性、特定目的適合性その他を一切保証しない。
- Model Weight、第三者Softwareおよび別License DefinitionをProject Licenseで上書きしない。
- 将来OSS化の検討は現在の権利を変更しない。

## 4. Snapshot

```text
Overview:
  docs/public/history/overview/
  overview_phase_1_ex_ja_20260727105501.md

Concept:
  docs/public/history/concept/
  concept_phase_1_ex_ja_20260727105501.md

Roadmap Before:
  docs/public/history/roadmap/
  roadmap_phase_1_ex_before_second_pass_ja_20260727105501.md

Roadmap Final:
  docs/public/history/roadmap/
  roadmap_phase_1_ex_final_second_pass_ja_20260727110347.md

Continuity Before:
  docs/project/current/history/project_continuity/
  project_continuity_master_phase_1_ex_before_second_pass_ja_20260727105501.md

Continuity Final:
  docs/project/current/history/project_continuity/
  project_continuity_master_phase_1_ex_final_second_pass_ja_20260727110347.md

Current Index Before:
  docs/project/current/history/index/
  documentation_index_phase_1_ex_before_public_reconstruction_ja_20260727105744.md

Current Index After:
  docs/project/current/history/index/
  documentation_index_phase_1_ex_after_public_reconstruction_ja_20260727110347.md
```

各Snapshotは作成時のStable原文と`cmp`一致を確認した。

## 5. Validation

```text
Stable Corpus Relative Links : 262 checked／0 missing
Demo Images                   : 6 files／6 README references
Old Identity                  : 0 files
Private User Absolute Path    : 0 files
CITATION YAML Parse           : pass
.DS_Store                     : 18 removed／0 remaining
Phase 1 Lossless Extraction   : 316／316 pass
Phase 1-ex Interim Extraction : 145／145 pass
pytest                        : 299 passed／3 deselected
ruff check                    : pass
ruff format --check           : 96 files already formatted
mypy                          : pass／96 source files
Git Operation                 : none
External Operation            : none
```

## 6. Known Pre-initial Commit Review

旧Lightning Basic PreviewのPlatform生成URLは、Phase 1のImmutable Evidence、Phase Stable CompilationおよびFinal Lossless内に18回、8 Fileで保持されている。Credentialは含まれず、Public Current／READMEには掲載していない。

Phase 1 Sourceを改変するとFinal Lossless Hashと監査整合が壊れるため、本作業では削除・置換していない。Initial Commit前のPublic Allowlist／Disclosure Reviewで、次のいずれかをユーザーが決定する。

1. Phase EvidenceとしてURLを保持したまま公開する。
2. Internal EvidenceをPublic Repository Allowlistから除外する。
3. Redacted Public Derivativeを別Artifactとして作り、原本は非公開保持する。

Testに`preview-password`が1件あるが、Basic認証境界を検証する明示的な架空Fixtureであり、実Credentialではない。

Model GGUFはProject外Storageへの`models` Symbolic Linkから参照できるが、Root `.gitignore`で`models`と`*.gguf`を除外している。Initial Commit前にもTracked CandidateへModelが入らないことを再確認する。

## 7. 結果

Public／Canonical／Legal Documentationの初版再構築と第2周は完了した。

これはPhase 1-ex完了、Public Allowlist完了、GitHub公開許可、Git初期化、匿名Public Demo公開または法的助言の完了を意味しない。

次は、Mac限定簡易Documentation RAG、Lightningの残Manual Validation、Git運用設計、Pre-initial Commit Refresh、Phase 1-ex Final Lossless、Final Review、Backupおよび公開Gateである。
