# Phase 2-E Claude Rework Cycle — Cross-provider Independent Review Evidence

```yaml
document_id: automation_governance_evidence_phase_2_e_claude_rework_cycle_20260815085208
status: interim_evidence
phase: phase_2
subphase: phase_2_e
from: Claude設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-15 08:52:08 JST
language: ja
related:
  - automation_governance_evidence_phase_2_e_claude_cross_provider_and_agent_automation_poc_20260815005913
  - automation_governance_evidence_phase_2_e_claude_completion_20260815075428
note: >
  ユーザーより「Agent自動化／Cross-provider実験は原則毎回記録してほしい」との明示指示（2026-08-15、
  本Task内会話）。以後、本SubphaseでRound（設計・実装・Rework等の主要区切り）が発生するたびに、
  Append-onlyで本カテゴリへEvidenceを追加する運用とする。
```

前回記録（`...completion_20260815075428.md`）はClaude単独でのCOMPLETE_CANDIDATE到達までを扱った。本記録は、その後Codexが独立Reviewを実施し、Required Reworkを差し戻した1サイクル分（P2E-CODEX-001〜004）を対象とする。

## 1. Cross-provider PoC：Independent Reviewが実際に機能した直接証拠

これは本実験系列で最も重要な新規Evidenceである。**Claude自身のIndependent Design ReviewおよびDesigner Conformance Reviewを経てもなお、Codexの独立Reviewが3件の実質的な技術的欠陥と1件のEvidence精度問題を検出した。**

検出内容：

1. **P2E-CODEX-001（実害あり）**：ユーザーの実Mac環境が実際に`sqlite-1`Schema・Conversation 5件を保持していることをCodexが確認し、Claude実装の`start_local_conversation_persistence()`がこの状態で起動不能になることを指摘した。Claude側のConformance Reviewはこの経路を通していなかった（Temporary Fixtureでの単純なEMPTY／READYケースしかTestしていなかった）。
2. **P2E-CODEX-002（設計と実装の乖離）**：Claude自身が設計したFR-1.1「DescriptorはCanonical Digestを含む」という要件に対し、実装が`canonical_digest=""`のまま登録する状態になっていた。Digest計算関数（`component_digest()`）自体は実装済みだったが、呼び出し忘れがあった。Claude側Testはこの不整合を検出していなかった（Testが`canonical_digest=""`を許容する形で書かれており、要件違反を隠蔽する形になっていた）。
3. **P2E-CODEX-003（Fail-closed設計の実質的な穴）**：DB列のCitation Schema VersionだけをチェックしてJSON Envelope内部の値を独立検証していなかったため、未来の未知Version（例：999）を持つRecordが正常なCitationとして受理されていた。Claude自身のTestは「DB列が極端に大きい値」というシナリオしかカバーしておらず、「DB列は正常・Envelope内部だけ異常」という組み合わせを見落としていた。
4. **P2E-CODEX-004（Evidence精度）**：Claudeが設計段階で書いたAcceptance Matrixは実装完了後にTest名の実態と乖離しており（Refactor・統合による自然なDriftだが、Claude側は事後に正本更新をしていなかった）、Completion Handoff／Conformance Reviewの「既存Test変更0」という記載も、実際には5〜6Fileが変更されていた事実と一致しない、意味の混同した表現だった。

**評価**：1〜3は、Claudeの自己Review（Independent Design Review、Designer Conformance Review）という**同一Provider内の多段階Review構造だけでは検出できなかった**種類の欠陥である。特に(1)は「実行環境の実際の状態（ユーザーの実DB）」という、Claude側からは観測できない情報にCodexがAccessしていたことが決定的だった（Codexの独立Review権限にはこの観測が含まれていたと推定される）。(2)(3)は、要件・実装・Testの三者が同じ思考の枠内で作られたために生じた「盲点の共有」であり、Codexという文字通り異なるProvider・異なるContextからのReviewが、その盲点の外側から指摘した点に価値がある。

これは、本実験の当初仮説「Cross-provider Independent Reviewは同一Provider内Reviewの限界を補う」を**実際のバグ検出という形で裏付けた最初の直接Evidence**である。中間記録・完了記録は主に「Docs-drivenのHandoffが機能するか」「Provider間で作業が引き継げるか」という接続性のEvidenceだったのに対し、本記録は「Cross-provider Reviewが独自の技術的価値を生むか」という、より実質的な問いに対するEvidenceである。

## 2. Agent自動化PoC：Reworkサイクルの自律完遂

Codexからの`codex_to_claude_phase_2_e_required_rework_handoff_20260815081954.md`受領から、次を単一Session内で自律完遂した。

```text
Handoff全文読了
  -> Required Reading Order（6文書）確認
  -> P2E-CODEX-001〜003 技術Rework（実装＋Test）
  -> P2E-CODEX-004 Evidence Correction（新規Append-only文書）
  -> Full Validation（671 passed／3 deselected、Ruff／Mypy／Node Clean）
  -> Rework Completion Handoff作成
  -> 「PHASE 2-E REWORK COMPLETE_CANDIDATE」報告・停止
```

境界遵守（Handoff第8節Prohibited全項目）：Stable正本非変更、既存History非改変（新規Correction文書のみ追加）、実`runtime_data/`非Mutation（全Migration TestはTemporary Fixtureのみ使用、実DBのMigrationは一度も実行していない）、Project Root外非Access、Git Mutation 0（実行したGit CommandはRead-onlyの`status`／`diff`のみ）。いずれも実測で確認済み（本サイクルのRework Completion Handoff第6節）。

ユーザーからの「重大な問題が発生した時だけ止めて」という一貫した運用方針のもと、3件の技術Findingと1件のEvidence Finding、合計4件を、いずれもUser Escalationなしに自Role Authority内で解消した。これは`transition_blocker_escalation_and_closure_contract_ja.md`が定義する「Responsible-role Ownedの問題をUserへMicro-escalateしない」という設計方針が、Cross-provider Reworkの受け入れという新しい状況でも機能したことを示す。

## 3. Constitution／将来設計への示唆（記録のみ）

- 今回Codexが検出した3件のうち少なくとも1件（P2E-CODEX-001）は、「実行環境の実際の状態を知っているProvider」と「実装したProvider」が異なることそのものが検出の決め手だった。将来、単一Providerが設計・実装・Reviewを全て担う構成では、この種の欠陥は原理的に見つかりにくい可能性がある。Cross-provider構成の価値は、Provider間の技術力差よりも「異なる観測範囲・異なるContext」に由来する可能性がある。
- Acceptance Matrixのような「実装前に書く計画文書」は、実装完了後に正本として鵜呑みにされるリスクを構造的に持つ。今後、設計担当者役は実装完了直後に自分でAcceptance Matrixの実在Test照合を行う工程を追加することが望ましい可能性がある（本サイクルではCodexの指摘で気づいたが、次回以降はClaude側で先回りできる）。

## 4. Status

```text
Current Point            : Rework Cycle 1完了（P2E-CODEX-001〜004 CLOSED）
Files Created／Modified   : 本Fileのみ（新規作成）
Validation                : N/A（Evidence記録）
Open Current Blocker      : NONE
Controller-owned Next Work: 次のRound（Codex Final Re-review、または追加Reworkがあれば）で追記
Deferred Evidence         : NONE
Exact Next Route          : Codexプロジェクト責任者兼設計統括者役Final Re-review
```
