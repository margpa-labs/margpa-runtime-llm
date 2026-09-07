# Phase 9-1 Claude Package 1 Lightweight Independent Judge Selection／Acquisition Exact Handoff

```yaml
document_id: phase_9_claude_package_1_lightweight_independent_judge_selection_acquisition_exact_handoff_20260902121740
document_type: exact_handoff
document_state: frozen_ready_not_started
language: ja
created_at: 2026-09-02 12:17:40 JST
phase: phase_9
program: phase_9_1
package: P9-1-JUDGE-PACKAGE-1
provider: Claude
role: 設計者兼実装者役
claude_weekly_availability_at_planning: 100_percent_user_reported_unexpected_reset
codex_weekly_availability_at_planning: 13_percent_user_reported_preserve_for_emergency
task_continuity: fresh_or_current_task_allowed_by_user_routing
overall_sequence: package_1_then_package_2
implementation_authority: bounded_manifest_and_registry_only
model_research_authority: true
network_authority: selected_public_model_research_and_download_only
project_root_external_artifact_authority: configured_model_root_only
real_model_load_authority: false
runtime_data_authority: false
git_authority: false
backup_authority: false
phase_9_closure_authority: false
phase_9_2_authority: false
maximum_claim: P9_1_LIGHTWEIGHT_INDEPENDENT_JUDGE_ARTIFACT_ACQUIRED_CANDIDATE_FOR_PACKAGE_2
```

## 1. Overall Sequence

Userは次の二つを一つの連続計画として承認している。

1. Package 1: 軽量な独立Judgeを比較・選定し、Artifactを取得する。
2. Package 2: Built-in／Main-shared Qwen／Selene／軽量Judgeを同一条件で比較し、共通Judge基盤、Provider固有差分、Judge／Repair／Rejudge、Semantic 109、最後にARGD／DAGDを含むMain Runtime Governance ENFORCEを成立させる。

本Handoffの実行対象はPackage 1だけである。Package 2の存在は最初から共有するが、Artifact取得後に一度Exact Returnし、Package 2専用Handoffで再開する。

Codex週間利用可能量はUser報告で残13%である。Routine Reviewや逐次確認のためにCodexを呼ばず、Repository内EvidenceとExact Returnを十分に残す。これはClaudeのAuthorityを拡張せず、Controller Reviewを省略したと主張する根拠にもならない。

## 2. Objective

Local MacでSeleneより軽く、Main Modelとは独立して動作できるLLM-as-a-Judge候補を小さなShortlistから選定する。License、公式Source、Artifact Identity、Runtime互換性およびResource見積りを確認し、既存の構成済みModel Artifact Rootへ選定Artifactを一つ取得する。

軽量JudgeはSeleneの代替削除ではない。Package 2ではSeleneも引き続き独立Judgeとして修復・比較対象に残す。

## 3. Minimum Reading

開始前の必読は次の3点に限定する。

1. 本Exact Handoff。
2. `docs/project/phases/phase_9/phase_index_ja.md`のCurrent StateとNext Authorized Sequence。
3. `docs/project/phases/phase_9/history/operations/phase_9_1_all_judge_operational_failure_common_substrate_hypothesis_and_rework_order_ja_20260902103228.md`の§4〜§8。

同一TaskのRecent Verified Contextを再利用し、旧Handoff、Phase 6〜8 Historyまたは全Docsを開始前に再走査しない。矛盾、Compaction、Authority変更またはCanonical State変更がある場合だけTargeted Re-readする。

## 4. Candidate Requirements

Shortlistは2〜4候補とし、最低限次を比較する。

- Main Modelとは別ArtifactとしてLoad可能な独立性。
- Selene 1 Mini 8B Q5より明確に小さいArtifact／Memory負荷。
- Local macOSと現行Runtime Stackで扱える形式。既存GGUF／llama.cpp経路を優先する。
- Typed JSONまたは厳格な構造化判定を安定して生成できる見込み。
- 日本語入力を含むJudge用途への適合性。
- Model Card、Release／Revision、License、配布元およびArtifact Filenameを追跡できること。
- 無償Local R&D／Portfolio用途と矛盾しないLicenseであること。
- Context上限、推奨Prompt形式、Quantization、Byte Size、Memory見積りを記録できること。

Popularityだけで選定しない。Judge向け性能Evidenceが弱い場合は、その不確実性を明示して比較する。

## 5. Work Units

### P1-WU-01 — Current Runtime Compatibility Freeze

既存Model Registry、Manifest、Artifact ResolverおよびDedicated Judge Adapterの必要InterfaceだけをTargetedに確認する。Source実装を変更せず、候補選定条件へ写す。

### P1-WU-02 — Shortlist／Decision

公式Model Card／Release／Licenseを優先して候補を比較し、一つを選定する。選定理由と不採用理由をEvidence付きで残す。

### P1-WU-03 — Artifact Acquisition

既存設定からModel Artifact Rootを解決し、選定した公式Artifactだけを取得する。既存Artifactを上書きしない。取得後にByte SizeとSHA-512を固定し、Download元、Revision、Filename、QuantizationおよびLicenseを記録する。

### P1-WU-04 — Minimal Registration Preparation

Package 2が即座に使える範囲で、必要ならProject側Manifest／Registry Entryだけを追加する。Runtime Load、Inference、Judge比較または共通基盤修復へ入らない。登録が不要ならSource Mutation 0を正直に記録する。

### P1-WU-05 — Recovery／Exact Return

Artifact、Docs、変更Path、未検証点、Package 2 Exact First ActionをLosslessに返す。Active Download、Load済みModel、Workerまたは一時Artifactを残さない。

## 6. Authority／Prohibitions

許可する。

- 候補調査に必要なPublic Network Access。
- 選定した一つの公式Artifact取得。
- 既存設定が示すModel Artifact Rootへの、そのArtifactだけのWrite。
- Package 2準備に不可欠なManifest／Registryの最小変更。
- Digest、License、Source、Compatibility EvidenceおよびRecovery Docs作成。

禁止する。

- Package 2のJudge基盤修復、Inference比較またはUI実装。
- Selene／Qwen3Guard／Main Artifactの削除、上書きまたは置換。
- User `runtime_data`、会話、Local CorpusまたはPersistent Storeへの接触。
- Dependency Install／Upgrade、Credential、課金APIまたは非公開Artifact。
- Git Stage／Commit／Push、Backup、Phase Closure、Phase 9-2開始。
- Provider Memoryへの正本保存。

## 7. Continuation／True Stop

通常の候補不適合、Download Retry、Minor Findingまたは比較上の不確実性では停止しない。次候補へ進み、Evidenceを増やす。

停止できるのは次だけである。

- Licenseまたは公式Artifact Provenanceを安全に確定できない。
- 取得にCredential／Payment／追加User Authorityが必要。
- 設定済みArtifact Rootが解決不能、または許可外RootへのWriteが必要。
- Canonical Stateが競合し、どのWorking Treeを継続すべきか復旧不能。
- Provider Resource Hard Stop。

Risk、Artifact Size、実装難度または後続Controller ReviewはStop Authorityを生成しない。

## 8. Verification／Return

最低限次を返す。

- Shortlist比較表と選定理由。
- Model ID、Release／Revision、公式Source、License。
- Artifact Path、Filename、Format、Quantization、Byte Size、SHA-512。
- Local Runtime互換性判断と未実行事項。
- Project側変更PathとFocused Static Check。
- Network／Artifact／Temporary Process Inventory。
- Package 2 Exact First Action。

最大Claimは`P9_1_LIGHTWEIGHT_INDEPENDENT_JUDGE_ARTIFACT_ACQUIRED_CANDIDATE_FOR_PACKAGE_2`である。Load／Inference／Judge成立、Phase 9-1 CompleteまたはClosureを主張しない。
