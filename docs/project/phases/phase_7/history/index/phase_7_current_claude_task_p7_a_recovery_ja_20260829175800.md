# Phase 7 Current Claude Task — Package P7-A Recovery（Attachment Sizing）

```yaml
document_id: phase_7_current_claude_task_p7_a_recovery_20260829175800
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 17:58:00 JST
active_contract: phase_7_claude_bounded_mvp_implementation_exact_handoff_ja_20260829172159.md
package: P7-A
```

## 1. Sizing対象

Architecture §6が定義する7項目を個別に判定する（Chat Composerからの汎用File Attachment、
P7-REQ-022／023）。

| 項目 | 判定 | 理由 |
|---|---|---|
| Transport only | 局所化可能 | 既存FastAPI Endpointへの`multipart/form-data`受信自体は小さい追加。 |
| Metadata persistence | 局所化可能 | 既存`sqlite_conversation_store.py`のTurn付随Recordパターンを転用可能。 |
| Safe local storage | 局所化可能 | `runtime_data_root`配下、既存Private File規約（`0o600`、Owned File検証）を再利用可能。 |
| Text extraction | 局所化可能（Text／Markdown限定） | 既存`DeterministicMarkdownChunker`はUTF-8 Text入力を前提にしており転用可能。 |
| RAG ingestion | 局所化可能 | P7-B以降で構築するLocal Corpus Registryへ、同一の登録経路として合流可能。 |
| Archive inspection | **Phase級** | Zip／Archive内部のSandbox展開、再帰Bomb対策、個別File種別ごとのContent-Type検証はP7-REQ-015のSecurity境界を満たすためだけでも独立したSubsystemが必要。 |
| Model-native multimodal | **Phase級** | 要件5節で明示Scope外（動画等のMultimodal分析）。画像／PDF等もLocal Modelの実際のMultimodal推論経路が未検証であり、Phase 7のResource（Disk約33GiB、Local Mac、金銭制約）下で新規に検証・実装することはPhase単位の工事になる。 |

## 2. Sizing Decision

```text
採用: Transport／Metadata／Safe Storage／Text Extraction／RAG Ingestionの5項目。
延期: Archive Inspection、Model-native MultimodalをPhase 10以降へ送る
  （Architecture §6「最初の5項目までが既存Boundary内で局所化できる場合のみ採用候補とする」
  に合致）。
```

さらに、Chat Composerへの汎用Drag&Drop添付Buttonそのもの（Per-turn一時Attachment、
Upload Progress UI、添付File種別の動的検出、複数File同時Upload、添付File単位の
個別Failure表示等）は、それ自体で新規Frontend Subsystem（Composer拡張、Upload State
Machine、Per-turn Attachment Persistence Schema）を要し、局所化5項目の組み合わせであっても
Chat Composer統合まで含めるとPhase級の工事量になると判定する。

**本Taskでの採用範囲**：汎用Chat Attachment Button（Composer統合、Per-turn一時添付）は
Phase 10以降へ延期する。局所化5項目自体は、P7-B（Local Corpus／Document Lifecycle）が
提供する「Local Document登録・更新・削除」機能（Settings経由、Text／Markdown限定）として
実現し、これによりP7-REQ-002（Local Document登録・更新・削除・Version／Digest追跡）を
Attachment Subsystem新設なしに満たす。P7-REQ-022／023（汎用File Attachment）自体は
Chat Composer統合を要する識別のため、その部分はPhase 10へ延期する。

## 3. Sizing Evidence

```text
判定根拠: Architecture §6 Attachment Sizing Boundary、Requirements §4 Scope外
  （MP4等動画Multimodal分析）、Resource Gate（Disk約33GiB、個人PoC、金銭・Hardware制約）。
延期Registry記録先: 本Package Recovery（本書）。P7完了後、
  `docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`のPhase 10候補区分
  （UF-HARD-*相当）へ、Controller Independent Review後に正式追記されることを想定する
  （本Claude TaskはStable未解決Registryへの直接書込み権限を持たないため、Evidence自体は
  本Recovery IndexとReturn Handoffへ記録し、Registry反映はController判断に委ねる）。
```

## 4. 本体への継続

Sizing完了により、Attachment（Chat Composer統合）を理由にPhase 7本体を停止しない
（Handoff §4 P7-A「Sizing Decision後は本体へ進み、Attachmentだけで全体停止しない」）。
P7-B（Corpus／Document Lifecycle）へ継続する。

## 5. Action Inventory（本Package内）

```text
Git Action: 0
Network Action: 0
Provider Memory Action: 0
Root外Read/Write: 0
Destructive/Irreversible Mutation: 0
```

Exact next action: Package P7-B（Local Corpus／Document Lifecycle）実装へ継続。
