# Design Governance Recovery Manifest

```yaml
document_id: design_governance_recovery_manifest
status: interim_current_state
recovery_state: ready_for_immediate_task_reconstruction
phase: phase_1_ex
phase_complete: false
created_at: 2026-07-27 12:13:43 JST
owner: 設計統括者役
language: ja
source_task_conversation_required: false
supersedes: null
final_phase_recovery_manifest: false
```

## 1. 目的

本書は、2026年7月27日の初回Documentation Corpus完成直後に、現在の設計統括者役Taskが停止、破損、Context Limit到達または再作成となっても、新しい設計統括者役Taskが旧Task会話へ依存せず、現在状態から即時に再開できるようにする臨時完全復旧Manifestである。

本書はPhase 1-ex完了版ではない。Phase 1-exは進行中であり、本書は`interim_current_state`として作成する。Phase完了、Backup取得、Git初期化、GitHub公開または匿名Public Demo公開を示さない。

本書だけでProjectの全詳細を置き換えるものではない。最短の復旧入口、正本、Integrity、Authority、現在地、残作業および次の安全な一手を固定し、詳細は指定したCurrent／Shared／Phase／Public文書から復元する。

## 2. 最上位Authority

```text
User Explicit Instruction
  → Task Role／Write Authority Policy
  → Active Phase Accepted Handoff
  → Documentation Structure／Task Operations
  → Documentation Rules
  → 設計統括者役による解決またはユーザーへのEscalation
```

設計統括者役は、ユーザーの許可なく次を変更してはならない。

- Append-only開発ログ
- Stable／History運用
- Lossless保持
- Docs Directory構造
- Task RoleとWrite Authority
- File Naming規則
- Git／Backup／公開方針
- License／利用条件
- External Action境界
- Model／Governance／LayerのON／OFF思想
- ユーザーがAcceptedしたRequirements、Architecture、ADRまたはRoadmap

便利さ、Git差分、重複削減、要約、可読性またはFile Sizeを理由に、既存情報を削除・圧縮・再解釈しない。

## 3. Project Identity

```text
Project Name       : margpa-runtime-llm
Display Name       : MARGPA Runtime LLM
Public Author      : Nazuna Research
Research Identity  : Nazuna Research
Project Root       : margpa-runtime-llm/
Current Phase      : Phase 1-ex
Last Planned Phase : Phase 10
```

MARGPA Runtime LLMは、Hugging Face由来の事前学習済みOpen Modelを利用し、Modelの外側から推論、文脈、監査、評価、修復および実行状態を統治する、Model-independent Runtime Governance型AI研究基盤である。

中心は単一ModelやChat UIではない。Model、Backend、Configuration、Governance Definition、Guardrail、Judge、Repair、RAG、Agent、Storage、UIおよびDeploymentを可能な限り分離し、交換、無効化、観測、介入および比較を可能にする。

最上位設計思想：

- 単一責任
- 疎結合
- 依存性逆転
- Port／Adapter
- Dependency Injection
- Module単位の交換・無効化・Test
- Framework固有処理の局所化
- 外部I/OとDomain Logicの分離
- 循環依存禁止
- Local／Cloud共通Application Core
- 研究・検証のための個別Layer ON／OFF

## 4. Current Phase State

```text
Phase 0                  : COMPLETE
Phase 1                  : COMPLETE／ACCEPTED
Phase 1 Backup           : COMPLETED／VERIFIED
Phase 1-ex               : IN PROGRESS
Initial Documentation Set: COMPLETE／VALIDATED
Git／GitHub              : NOT STARTED
Anonymous Public Demo    : NOT RELEASED
Mac Documentation RAG    : NOT IMPLEMENTED
Phase 1-ex Final Lossless: NOT CREATED
Phase 1-ex Final Backup  : NOT CREATED
```

README上部の現在地は、次に統一した。

```text
Phase 1-ex / 最終予定 Phase 10
```

Phase 1は完了・Accepted済みである。Phase 1-exは初回公開前の再整備Phaseであり、Docs完成だけではPhase 1-ex完了にならない。

## 5. 2026-07-27 Documentation Completion State

ユーザーが依頼した初回Documentation Corpusは完成している。

- Project Continuity Master第1周／第2周
- Public Roadmap第1周／第2周
- Current Canonical Set
- Phase 1 Final Lossless Compilation
- Phase 1-ex Interim Lossless Compilation
- Shared Stable Set
- Public Overview
- Public Concept
- README
- LICENSE
- TERMS_OF_USE
- NOTICE
- CITATION
- Final Documentation Validation

Source Freeze：

```text
Docs        : 493
Demo Images : 6
Total       : 499
Validation  : 499／499 pass
```

Lossless：

```text
Phase 1    : final／316 of 316 pass
Phase 1-ex : interim／145 of 145 pass
```

Final Validation：

```text
Selected Stable Files       : 21
Relative Links              : 286／286 pass
Missing Links               : 0
Demo Images                 : 6／6 pass
Old Identity／Private Path  : 0
.DS_Store                   : 0
CITATION Parse              : pass
Phase 1 Lossless Extraction : 316／316 pass
Phase 1-ex Extraction       : 145／145 pass
Runtime Tests               : pass
Ruff                        : pass
Mypy                        : pass
```

Final Validation Evidence：

```text
docs/project/phases/phase_1_ex/history/operations/
documentation_reconstruction_final_validation_20260727110834.md
```

## 6. Mandatory Reading Order

新しい設計統括者役Taskは、次の順で全文を読む。

1. `docs/project/current/documentation_index_ja.md`
2. `docs/project/current/project_continuity/project_continuity_master_ja.md`
3. `docs/project/shared/design_governance_handoff/design_governance_handoff_ja.md`
4. 本Recovery Manifest
5. `docs/project/phases/phase_1_ex/phase_index_ja.md`
6. `docs/public/roadmap_ja.md`
7. `docs/project/current/requirements/requirements_specification_ja.md`
8. `docs/project/current/architecture/system_architecture_ja.md`
9. `docs/project/current/architecture/technology_selection_ja.md`
10. `docs/project/current/architecture/basic_design_ja.md`
11. `docs/project/current/governance/runtime_governance_specification_ja.md`
12. `docs/project/shared/conventions/documentation_rules_ja.md`
13. `docs/project/shared/operations/documentation_structure_and_task_operations_ja.md`
14. `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
15. `docs/project/phases/phase_1/phase_index_ja.md`
16. 対象作業に必要な最新Accepted Handoff／Review／Status

Raw Historyを最初から全件読む必要はない。要件の由来、矛盾、旧判断、失敗Evidence、変更前原文またはLossless性を検証する場合に対象Historyを読む。

## 7. Canonical／Stable Integrity

### 7.1 Root／Public

| Path | SHA-512 |
|---|---|
| `README.md` | `95badf6dd997dd8620c287c1d96719243eaf97386c477da535362d024039d74a3c43e2d2465cb5235e38515bfeb6752c6c144328b694442282dc0100920d4457` |
| `LICENSE` | `8d378c4c2994c3e55bb2ccaae27367eb7e66c5da04d028a0d73d727a330ab1ebf0d71f98c9d4f667f2fe6c43881f50d2e5d1fab74b5fd908e357a3db6e867485` |
| `TERMS_OF_USE.md` | `83ee862ca210f03e50c32a289f4d45f36335678adb377a0bfaac25a0b108d7eb52f1ec5f028a8f8167239f440992fe4e3e9771b244cde492f0cd19d2a4f3c1da` |
| `NOTICE.md` | `8ae8440b7fea8c10663608deee3b352fc960a25fb8f4197518dd6ceb9c60179011b1bbaefc8756fe9add0714020d50fcdd929615c91eb7913882076e027af0c3` |
| `CITATION.cff` | `9260fd358f8821df72a28c022b30630f948c91ae7611d132f7a777d343a0aade8ce2b3714773122267f173521b6a5968c397fa5643a07676a80278be2a5f86d1` |
| `docs/public/overview_ja.md` | `5866fceee5f43775d880b64fc6f0956c23efde8e81f6ba2f8b7774ba11d90a171e381d5706e01e29bc05dde932943c97c1563e34dc7964fbd81fa10e3957bf71` |
| `docs/public/concept_ja.md` | `7ac64ccaa77c3dcce6bcda6b7c04f0af0b94759632051bf8cf0054e4e70ba38c1dfff602ddb1717187b8af32066448ccfa87e2027f3fd55d4f1b4948c5cb21d6` |
| `docs/public/roadmap_ja.md` | `0a3fbaac2cf247f0999213d3c8866a5537b8112a656dee7b9588c92c76a6a3b892799da938c6415fe8bffff9fd378b4726f0f79cd01bd4ed71c8434796f88e02` |

READMEのHashは、本Recovery PointでPhase表示を追加した後の値である。

### 7.2 Current Canonical

| Path | SHA-512 |
|---|---|
| `docs/project/current/documentation_index_ja.md` | `27fcbf1cba153b9760b7bc75c46efda2b624bb39e7c38529fe6831f3d805f3901763c1a64e23bcf5d407a5f94f1d52b9f888e35fe8ee888bc7acc4d9077f076b` |
| `docs/project/current/requirements/requirements_specification_ja.md` | `71cd545dc1c0768dc0cbd27291c79175790d199698743b307a4aaaa11e8ce2124faa102d18c1588bf9e66334a4d5a543b44d5ffd8f152f99df00cc5ebbe373c1` |
| `docs/project/current/architecture/system_architecture_ja.md` | `6f2e23c4c03ff0cbe69db7aa83ccf85f52edfa7b2d2ab0241eca7e28abfb0c15a555cc42f40a3bd637415fdd622dd9b6fc0dddba6628f15f06bf26746a502c4b` |
| `docs/project/current/architecture/technology_selection_ja.md` | `5b310e37d395f34ac59fff36e91e8d2bcc2aaa3256cac465c7b9079702ac1aee92d62a38c34b4c2624ddaffc24e8eb143a596acfcc7fd9eb1731e7beb8858a75` |
| `docs/project/current/architecture/basic_design_ja.md` | `f5a91aa162860ccd0348d8ae4e73fa272e916578d1bd56cca9dae9b87738153c6f3dae8cea39917bd70eb2547b006cf68686690a69ee0fa919e5dd80affa7215` |
| `docs/project/current/governance/runtime_governance_specification_ja.md` | `39b33fd6ab35fa1f490e9aeb90967ba662bfe533c37d9409a448d20673048d3f77b71a8cb3c6b2aa28a3949e514ba47530d1cd7d961fa8abcf8d11983625c9f6` |
| `docs/project/current/project_continuity/project_continuity_master_ja.md` | `7c6c1faba5f1adc2f1f8a9429ffd4e35cd7a6df4e233bb6b793025c0131e5a8c19c0775957778a493d3e8b5c1f26a369246340f05a35c76ec0e026b14a69a740` |

### 7.3 Shared

| Path | SHA-512 |
|---|---|
| `docs/project/shared/conventions/documentation_rules_ja.md` | `fe536ec8975d60d9142b79b7bbf220297ba49f8bb7ecd7b24a7e2dad063b6027f61c1f634affffc9f2e1cc90cf98906ae1930400dc4524b88c9d201924a8e122` |
| `docs/project/shared/operations/documentation_structure_and_task_operations_ja.md` | `aae515d3a2ffe983b5a83b88b7a161fef701ed5e4faacbb5081d17d73e462e030954ce3fc2f2ccc98e0f6a342ffcda4d9d11dbb58b41d06d3b44bde89cb3c326` |
| `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md` | `53815d85328f04ed32d6660f621910b3a334019b0724baffa2117c842f67ba74d19a8d935c5b596b4a3f163ccc636871d9aa3062e114d0009683f52e0f805733` |
| `docs/project/shared/design_governance_handoff/design_governance_handoff_ja.md` | `68cdd050d5b3902249d04ec7b7262946645a03dc4ddfeb20d708c6bfb939a08b798007052e7e8e3c38f66f8278de43b44c339d9ef8d7822b4a460b8773d7e05d` |

### 7.4 Phase／Lossless

| Path | SHA-512 |
|---|---|
| `docs/project/phases/phase_1/phase_index_ja.md` | `a6bba0f365a208bc519ab14ae03ef20e4409df58e084bc3bebbe69884ed4c70e4d2ac27e67f9b7c32fd2b0cca77509b5fbb16fd7f65bcc30dc3037a191a9efc1` |
| `docs/project/phases/phase_1/lossless/phase_1_lossless_ja.md` | `f0e5875b28d06425a9a5eb31c2004c976738f0236fc45acfd7712d6673d2d60f449f44bc6193643220590644369762bc2f2c9cf2aabf90bf0577084366793705` |
| `docs/project/phases/phase_1/lossless/phase_1_lossless_manifest.json` | `4caec1970a190010503dfb1a6caea5075a0c9779352ee6c0129af1007f78bb696990c5d6fab5dba174e64fbca6210132723cf8dbe10c7bdc4f03c1ea95d8d543` |
| `docs/project/phases/phase_1_ex/phase_index_ja.md` | `28eeafd888b1c983d8b770257c3f58b9f8393d2b0b6f1000578ad3c51b3fac5b743c0a811c19433ea7a566a6308df61504b0d19156262f89cd4bdf7a99fcf617` |
| `docs/project/phases/phase_1_ex/lossless/phase_1_ex_interim_lossless_ja.md` | `1dfc8fc71eea947e61c75502cadc31b5d993f4a9834b23571cacf65aacf99a11913bb3333bdcb26dfb55a72a2f5120f623fb925b282cea2968fe026ab0cfc38c` |
| `docs/project/phases/phase_1_ex/lossless/phase_1_ex_interim_lossless_manifest.json` | `844e8407811acbecedf990eb74092743b8eab3d13eb00ae79620a21f6e299f15910a92a20dbe74cd225c32a85f4207500dfa9124735cb1024ab97ce85c472a1f` |

Phase 1-ex Indexは、本Recovery Manifestと変更Recordを追加する直前のHashである。Current Documentation Indexは本Manifestへの導線を追加した後のHashである。後続のPhase Index更新はAppend-only Snapshotで追跡する。

### 7.5 Source／Validation

| Path | SHA-512 |
|---|---|
| `docs/project/phases/phase_1_ex/history/operations/documentation_reconstruction_inventory_20260727093727.md` | `9f570cc779aa13f291ee4bb33562deed266b0987cbb551b635d2635c5f5f455a918147a30011514a64dddcbc74cc1abe693fdf7a28fb9eea511b6b7d5840eafe` |
| `docs/project/phases/phase_1_ex/history/operations/documentation_reconstruction_source_inventory_20260727093727.json` | `c83b92063db185324feb1b4a907b79ddc72dac7eb0b17948fab77c8ba3dea5363fef6a06ee7a73439002aa1994c0a1a2e8a672d50824ab768b186a14d64aa513` |
| `docs/project/phases/phase_1_ex/history/operations/documentation_reconstruction_final_validation_20260727110834.md` | `802755d696a2f3f2f2e078ef02e6a960e20166b5295d1db2a1d029477c246830137d43893668c4d5e1825b873807290abd4295eeb7e0d1b9d87d577c92d605c0` |
| `docs/project/phases/phase_1_ex/history/documentation_index_20260727110950.md` | `8f5014b0f36d8e0070cfa017a95518d0b524ef12582801df03f27744096d6471e2fd7f600e01c9ac3777c46fe850da27794d6d0c18f571b66813416fb973a71c` |

## 8. Runtime／Model Baseline

### 8.1 Local Main Model

```text
Model Repository : Qwen/Qwen3-4B-GGUF
Upstream Model   : Qwen/Qwen3-4B
Artifact         : Qwen3-4B-Q4_K_M.gguf
Format           : GGUF
Quantization     : Q4_K_M
Backend          : llama-cpp-python 0.3.34
Local Python     : 3.13.14
Local Hardware   : Apple M2 Pro／16GB
Acceleration     : Metal
Context Load     : 4096
Default Response : ja
Default Max New  : 2048
```

Model ArtifactはGit、DocsまたはPhase Source Archiveへ含めない。Project Rootの`models/`は外部Model RootへのSymbolic Linkとして運用できる。Model Root、RegistryおよびAdapterを分離し、Model Filenameを正規化する必要はない。

### 8.2 External Runtime

```text
Platform          : Lightning AI Studio
OS／Architecture  : Ubuntu Linux x86_64 Container
Verified Python   : 3.12.11
Verified Runtime  : Pure CPU
GPU Candidate     : Tesla T4／CUDA
GPU Current Scope : deferred／cost-sensitive
Preview Access    : Basic Preview accepted
Credential Source : Managed Secrets／Environment only
Traffic-aware Wake: manual validation pending
```

LightningでのPlugin Install、API Builder設定、Public URL発行、Sleep／Wake、Managed Secrets、Machine／Credit操作はユーザー担当である。実装者役または設計統括者役が勝手に外部操作しない。

過去のLightning URLはImmutable Evidenceに残す。将来URL変更時はHistoryを改変せず、READMEと現在有効なIndex／案内だけを新URLへ更新する。

### 8.3 Model Candidates

```text
Main  : Qwen3-4B-GGUF Q4_K_M
Guard : Qwen3Guard-Gen-0.6B-GGUF Q8_0
Judge : Selene-1-Mini-Llama-3.1-8B-GGUF Q5_K_M
```

Guard／JudgeのGGUFでCapability不足を感じた場合は、Hugging Faceの通常Weight版を別Adapterで使用する。Phase 1ではMain Modelだけを使用する。

## 9. Governance Baseline

ARGD／DAGDを単なるSystem Promptとして全投入せず、Model外側のInference Control Planeとして扱う。

```text
Governance Definition
  → Loader／Validator
  → Compiler
  → Governance Plan
  → Shared Control Plane
  → Lightweight Governance Point
  → Model／Guardrail／Judge／Agent／Tool／Repair等
```

全Governance Definitionが空、JSONが一件もない、未知のGDだけがある、Schema不明、名前が既知GDと無関係という状態を許容する。ARGD／DAGDを含め、Definition名や個数をCoreへHardcodeしない。

Layerと各Layer専用Governanceは、原則として個別に次のModeを持つ。

```text
off
observe
enforce
```

依存、排他、Degraded Mode、Runtime変更可否、Restart要否をSchema Validationする。Runtime Governance、Guardrail、Tool PermissionおよびModel Policyを同一責務に混ぜない。

Guardrail／Judge／Repair／Agent／RAG／ML／定量計算／定性計算／研究・開発者Modeは将来Phaseで追加する。

## 10. External R&D Hooks

Phase 10以降または本Project一通り完成後に、別Projectで開発する次のR&D機構を疎結合に接続できるHookを維持する。

### EASA

```text
Exception Aware Safety Architecture
例外認識型安全統治機構
Research Domain: AI Safety Governance
```

内部安全傾向、周辺安全制御およびComposite Safety Behaviorを、例外認識を含めて統治する。

### DLAGSA

```text
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構
Research Domain:
  Multi-Agent Governance,
  Distributed Accountability,
  and Safety Assurance
```

複数の判断・実行・検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う。

### OCILNS

```text
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網
```

人、AI、Tool、外部System間の認知対話を、検証、参照、継承、監査および改変検知可能な証跡単位として扱う。

三機構は独立ModuleとしてON／OFF可能にする。公開文書では名称、研究領域、方向性およびHookだけを示し、未公開核心を推測・生成しない。

## 11. Documentation Rules

- Project Rootは`margpa-runtime-llm/`である。
- ユーザーが`docs/`とだけ述べた場合、`margpa-runtime-llm/docs/`を指す。
- Task間の情報伝達、進捗、HandoffおよびReviewは原則Docsを使う。
- Docsは基本Read-onlyであり、Write Authority外のTaskが勝手に編集しない。
- StableはTimestampなしの固定名を使う。
- Stable変更前後の原文をHistoryへ完全保存する。
- Timestampを付けるのはHistory SnapshotとEvent Artifactだけである。
- HistoryはAppend-onlyで、編集、削除、圧縮、置換しない。
- 内容変更時は新TimestampのEvent／Indexを作る。
- 古い文書へSuperseded表記を追記しない。
- 新Indexから旧文書の状態を示す。
- 新しいIndexが最新である。
- Current、Shared、Project Continuity、LosslessおよびDesign Governance Handoffは累積・自己完結とする。
- Diff-only禁止。
- Publicも原則追加式とする。
- 日本語正本を優先する。
- Current／Public英語版はPhase 1-ex後半で再判断し、作る場合は日本語版と同粒度にする。
- ユーザーの許可なく運用を変更しない。

## 12. Role Authority

### 12.1 設計統括者役

Project全体、Cross-Phase、Current、Shared、Phase構成、Final Review、Continuity、Backup／Git／Release設計を担当する。Phase 1-exではPhase専用設計も兼ねる。

### 12.2 Phase別設計者役

Phase 2以降に必要に応じて配置する。担当PhaseのRequirements、Architecture、ADR、Operations、Handoffを担当する。Current、Shared、他PhaseおよびPublicはRead-onlyである。

### 12.3 実装者役

`src/`、`tests/`、`scripts/`を担当する。Accepted Handoffとユーザー許可がある場合だけ`config/`等を変更する。Current、Shared、Public、Requirements、Architecture、Governance、ADR正本はRead-onlyである。

### 12.4 対外Docs役

将来、`README.md`、`LICENSE`、`TERMS_OF_USE.md`、`NOTICE.md`、`CITATION.cff`および`docs/public/`を担当する。Phase 1-ex完了まではユーザー指示により設計統括者役が全Docsを作成する。

## 13. License／Disclosure State

現状はResearch Previewである。

```text
GitHub         : 閲覧・評価のみ
Demo           : 明示された範囲で操作可能
Other Use      : 原則禁止
Warranty       : 一切なし
Public Identity: Nazuna Research
```

動作、互換性、正確性、安全性、完全性、可用性、特定目的適合性、研究結果または出力品質を保証しない。全Layerを研究のためON／OFF可能にする設計であるため、無効化構成の安全性を保証しない。

Model本体、`.venv/`、Cache、Secret、Credential、実会話Log、個人情報およびLocal Overrideを公開Artifactへ含めない。

GitHub Ownerは`margpa-labs`、公開Author／Research Identityは`Nazuna Research`とする方針である。ただしGit運用は未決定・未開始である。

## 14. Current Open Work

優先順はユーザーが次に明示する。現在の残作業集合は次である。

1. Mac限定簡易Documentation RAG
2. External RAG Adapter Hook
3. `docs/`不在時の明示的Unavailable応答
4. Lightning Traffic-aware Wake-upのユーザー手動実証
5. Basic Previewと分離したPublic Demo境界
6. Git運用設計
7. `.gitignore`、公開Allowlist、Secret／Identity／Artifact Sanitation
8. Initial Commit直前のCurrent／Shared／Public／Continuity再照合
9. Phase 1-ex Final Lossless Compilation
10. Phase 1-ex完了版Design Governance Recovery Manifest
11. Final Review
12. ユーザー手動Test Acceptance
13. Phase 1-ex完了・次Phase移行可能宣言
14. Phase 1-ex Backup
15. ユーザー許可後のGit初期化、Commit、Tag、Remote、Push

## 15. Known Limitations／Deferred Items

- Lightning Pure CPUは生成が遅い。
- Traffic-aware Wake-up、Cold Start、Sleep中の外部URL起動、URL永続性およびCredit条件は手動実証前である。
- iPhone／Responsive UIは後続Phase。
- Streaming中はMarkdown Raw表示があり、Completion後に変換する現状。
- Markdown Table表示、Code Block分離、Code Block専用Copyは後続UI。
- Thinking表示はModel内部生成文字列であり、正しさまたは真の内部思考を保証しない。
- Thinkingを有効にしたままMax Tokenが小さいとFinal Answer前に上限到達する。
- Thinking内容のResponse Language強制は未保証。
- Linux／Windowsの完全自動Profile Routingは将来拡張。
- Setup RecipeのNative Backend再Buildは通常同期として重い。
- 不正Environment設定と別Field CLI Overrideの同時指定ではError原因分類が不正確になり得る。
- Audit、Governance、Guardrail、Judge、Repair、RAG、AgentはまだMVPの後続範囲。
- Model性能は小型量子化Modelと現在Hardwareの制約を受ける。

## 16. External／Destructive Action Boundary

次はユーザーの明示許可なしに行わない。

- Git初期化
- Commit／Tag
- Remote設定
- Push／Pull Request
- GitHub Repository変更
- Lightning Plugin Install
- Lightning API Builder設定
- Public URL発行
- Managed Secret作成・変更
- Machine／GPU／Credit変更
- Model Download
- Dependency Install
- File削除
- History移動・削除・圧縮
- License変更
- 匿名Public Demo有効化

Read-only確認、Docs整合性検証およびユーザーが明示許可したDocs更新は、Authority範囲内で実施できる。

## 17. Next Safe Action

新Taskは、最初に本Manifest記載のPathが存在すること、Stable HandoffとCurrent Indexが読めること、およびPhase 1-exが未完了であることを確認する。

次に、ユーザーへ現在状態を次のように報告する。

```text
Phase 1は完了・Accepted済みです。
現在はPhase 1-exです。
初回Documentation Corpusは完成・検証済みです。
Git／GitHub、Mac簡易Documentation RAG、Lightning Traffic-aware Wake-up手動実証、
Phase 1-ex Final Lossless、Final ReviewおよびBackupは未完了です。
次に指定された作業だけを進めます。
```

推測で次工程を開始しない。ユーザーが直前に指定した作業が存在する場合は、その作業を優先する。

## 18. Fresh Task Recovery Prompt

新しい設計統括者役Taskへ渡す最小Prompt：

```text
あなたはMARGPA Runtime LLMの設計統括者役です。
Project Rootはmargpa-runtime-llm/です。
まず次を読み取り専用で全文確認してください。

1. docs/project/current/documentation_index_ja.md
2. docs/project/current/project_continuity/project_continuity_master_ja.md
3. docs/project/shared/design_governance_handoff/design_governance_handoff_ja.md
4. docs/project/shared/history/design_governance_handoff/
   design_governance_recovery_manifest_20260727121343.md
5. docs/project/phases/phase_1_ex/phase_index_ja.md
6. docs/public/roadmap_ja.md
7. docs/project/shared/conventions/documentation_rules_ja.md
8. docs/project/shared/operations/documentation_structure_and_task_operations_ja.md
9. docs/project/shared/task_roles/task_role_write_authority_policy_ja.md

確認後、Project Identity、Phase状態、完了済みDocs、残作業、Authority、
Git／External Action境界、次の安全な一手を報告してください。
ユーザーの許可なくDocs運用、History、Git、外部Service、Licenseまたは公開境界を変更しないでください。
```

## 19. Reconstruction Acceptance

新Taskが旧Task会話なしで次を説明できれば、即時復旧`pass`とする。

- 何を、なぜ作っているか。
- 現在はPhase 1-exで、Phase 1-ex未完了であること。
- 初回Documentation Corpusは完成・検証済みであること。
- Current、Shared、Phase、Public、History、Losslessの違い。
- 現在有効なRequirements、Architecture、Governance、Roadmap。
- Model、Backend、Local／Lightning Runtime。
- Role Authority。
- License／公開境界。
- GitとExternal Operationが未許可であること。
- 残作業と次の安全な一手。
- Phase 2以降にPhase別設計者役を復元する方法。

解決不能な項目が一つでもある場合、推測で埋めずOpen Findingとしてユーザーへ報告する。

## 20. Manifest Boundary

本書作成後に追加されたDocs、Code、Test、External Stateまたはユーザー決定は、本書へ自動反映されない。後続作業ではStable Handoff、Phase Indexおよび新しいAppend-only Documentation Index Snapshotを優先し、Phase完了時に最終Recovery Manifestを新規作成する。

本書、更新前後Handoff Snapshot、README Snapshot、変更Record、Phase IndexおよびDocumentation Index Snapshotを一組として、2026-07-27 12:13:43 JST時点の臨時完全復旧点とする。
