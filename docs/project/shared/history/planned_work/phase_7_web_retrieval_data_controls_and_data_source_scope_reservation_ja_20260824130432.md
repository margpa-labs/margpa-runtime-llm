---
document_id: phase_7_web_retrieval_data_controls_and_data_source_scope_reservation_ja_20260824130432
status: reserved_not_started
document_type: append_only_planned_work_scope_reservation
language: ja
recorded_at: 2026-08-24 13:04:32 JST
from: user
to: project_responsible_and_design_governor_role
decision_authority: user
applies_to:
  - phase_7_rag_and_data_governance
  - phase_7_web_retrieval
  - phase_7_data_controls_ui
  - phase_10_plus_data_quality_and_label_governance
  - phase_10_plus_enterprise_licensed_data
default_mode: "OFF"
current_implementation_authorized: false
network_action_authorized: false
provider_contract_authorized: false
training_authorized: false
git_mutation_authorized: false
---

# Phase 7 Web Retrieval／Data Controls／Data Source Scope予約

## 1. User Decision

Phase 7では、古いModel Weightだけに現在情報を依存させず、Runtimeで外部情報を検索・取得・評価・引用できるWeb Retrievalと、研究Dataの取得・保存・利用目的をユーザーが制御できるData Governanceを実装対象へ含める。

学習Data Source候補のうち、**提携先・License契約経由のData連携はPhase 10以降へ延期**する。現在の個人開発段階で企業契約、専用Archive、商用DatasetまたはEnterprise Connectorを前提に設計・実装し、そのために利用可能量を消費しない。

それ以外の次の要素はPhase 7 Scopeへ含める。

- 公開Web情報のRuntime検索、取得、正規化、評価およびCitation。
- Local／Public Corpusの登録、更新、RetrievalおよびProvenance。
- ユーザー提供Data、明示Feedbackその他のHuman-generated Dataの最小管理境界。
- AI-generated／Synthetic Dataの生成主体識別、最小来歴および将来利用のためのExport Seam。
- Dataの保存、利用目的、Retention、ExportおよびDeleteを制御するUI。

一方、Dataset全体を対象とするCleaning、Data Quality、Label Governance、Training／Evaluation Eligibility、Annotator GovernanceおよびAdjudicationは、Phase 9までのPlatform土台完成後に扱うべき独立R&D Scopeとして、Phase 10以降へ延期する。

## 2. Phase 7で行うこと／行わないこと

Phase 7で行うのは、現在の回答へ根拠を与えるRuntime Retrievalと、将来の評価・研究・学習へ利用可能なDataを**出所と利用目的付きで管理する基盤**である。

Phase 7完了をもって、Qwen、DeepSeekその他のModel Weightが自動更新・再学習・Fine-tuningされたとは扱わない。Chat、FeedbackまたはSynthetic Dataを保存しただけで「Modelが学習した」と表示してはならない。

```text
Phase 7:
  Runtime Web Search／RAG
  Corpus／Data Provenance
  Human Feedback／Synthetic Dataの識別・Consent・最小Provenance
  Evaluation／Future Training Export Seam
  Data Controls UI

Phase 7では行わない:
  Model Weightの無断Training／Fine-tuning
  User DataのDefault Training利用
  Full Dataset Cleaning／Label Governance
  Training／Evaluation Eligibility判定
  企業提携Data／有償License Dataの取得
  Provider契約、課金、Credential作成の自己許可
```

実際のTraining／Fine-tuning／Model Promotionは、別PhaseのExact Design、Resource、License、Privacy、Quality、RollbackおよびHuman Gateを成立させてから実施する。

## 3. Data Source Class

Phase 7のData正本では、少なくとも次を混同しない。

```text
public_web
local_corpus
public_project_corpus
user_provided
human_feedback
synthetic_generated
partner_licensed        # Phase 10以降／Phase 7ではUnavailable
```

各Data／Chunk／Evidenceへ、Phase 7で必要な範囲のSource Class、Canonical URLまたはDocument Identity、取得時刻、公開／更新時刻、Content Digest、License／Terms状態、生成主体、生成Model、Transformation履歴、採否理由およびCitationを保持する。

これはRuntime Retrievalと将来拡張に必要な最小Provenanceであり、DataがClean、Label Correct、Training Eligible、Evaluation EligibleまたはProduction Eligibleであるとの認定を意味しない。

`partner_licensed`はSchema／Extension Seamの予約に留め、Phase 7で実Provider、契約、CredentialまたはDataをBindingしない。

## 4. Web Retrieval

既存のWeb Retrieval予約を継承し、Phase 7では次をExact Design候補とする。

- Vendor非依存の`WebSearchPort`、`WebFetchPort`およびContent Normalizer。
- Search Snippetと取得本文を別Evidence Classとして扱う。
- 公式Source、一次Source、二次Source、一般WebおよびSource不明をAuthority／Quality Classで分離する。
- URL、Canonical URL、Title、Provider、取得時刻、公開／更新時刻、Content Type、Digest、採用ChunkおよびCitationを追跡する。
- Model Knowledgeと取得Sourceが矛盾した場合、矛盾をJudge／Repairへ渡す。
- ENFORCE時、必要なCurrent Evidenceを取得できない場合は、未確認事項を確定事実として断言させない。
- Document Prompt Injection、SSRF、Secret／PII送信、Private Network、危険Scheme、過剰Redirect、巨大ResponseおよびCost超過をGoverned Runtime側で拒否する。
- Model自身へ無制限のNetwork／Browser Authorityを与えない。

検索起動とGovernance強度は一つの値へ混ぜない。

```text
Search Activation:
  disabled | manual | automatic

Web Evidence Governance:
  OFF | OBSERVE | ENFORCE
```

初期値は両方ともOFF／disabled相当とし、OFFではNetwork Call 0を不変条件とする。OBSERVEでは、外部送信なしでSearch Intent／Query Candidate／必要根拠を観測できる構造を候補とする。実Query送信を伴う挙動は、Manual操作またはExact Policyを満たしたAutomatic経路へ限定する。

## 5. Settings第三領域「データコントロール」

Settingsに第三のTop-level領域として、ユーザー向け機能名**「データコントロール」**を追加する候補をPhase 7へ予約する。短い機能名だけを流用し、他製品の説明文、画面配置、Icon、Visual DesignまたはTrade Dressを複製せず、MARGPA固有の情報構造とUIとして実装する。

最低限のControl候補は次である。

- Chat履歴の保存状態とRetention。
- Local RAG／Web取得Data／Citation Evidenceの保存状態。
- Web Searchの有効化、Manual／AutomaticおよびGovernance Mode。
- Search Providerへ送信可能なQuery／Conversation Context範囲。
- Recordingの`OFF／metadata／full`とProtected Research Captureへの導線。
- User Feedback／評価Labelの研究Dataset利用可否。
- Synthetic Data生成および将来Training Exportへの利用可否。
- Data Source Class、保存場所、容量、件数および最終更新時刻の表示。
- Conversation／Retrieved Data／Evidence／DatasetのExportおよびDelete。
- 外部送信、保存、Dataset化または将来Training利用前の明示Opt-in。

User Data、FeedbackおよびSynthetic Dataの研究・Training利用は初期値OFFとする。Conversationの通常利用、履歴保存、Evaluation利用、Dataset ExportおよびModel Training利用を別Consent／Purposeとして扱い、一つのONで全用途を許可しない。

## 6. Current Model Failureとの関係

Qwen／DeepSeekの古いKnowledgeをRuntime Web Retrievalで補完できる可能性はあるが、次を分離する。

- DeepSeekの同一出力反復、Token／Template／Sampling異常はWeb検索では修正できない。
- Qwenが提示済み公式Evidenceを無視して根拠のない断定を行う問題は、RetrievalだけでなくEvidence Contradiction、Judge、RepairおよびENFORCE経路の修正が必要である。
- Phase 7は「検索結果をPromptへ入れた」だけでAcceptedにせず、Sourceに基づく最終回答、Citation、矛盾検知およびRepair成立まで検証する。

`current`、`latest`、`today`、`official`その他の鮮度・Authority要求、ModelのKnowledge Cutoff外候補、明示的なUser Search要求およびUnsupported Claim候補をAutomatic Search Triggerの設計対象とする。

## 7. Phase 10以降へ延期するData Quality／Label Governance

Phase 9までのRuntime Governance、RAG、Agent／Tool／Memory／HandoffおよびExperiment Platformの土台が完成した後、Phase 10以降で、Data Cleaningを単なるFile整形や削除ではなく、**Data／Label／Provenance／Eligibilityを統治する独立System**として設計する。

最低限、次を対象とする。

- Source contamination：低品質Source、Spam、誤情報、AI生成低品質Data、転載Loop。
- Duplicate／Near-duplicate：特定Patternの過重学習や評価歪曲を生む重複。
- Label noise：曖昧な定義、誤Label、Annotator間不一致。
- Policy drift：Label基準、Safety基準またはGuideline Revisionの時系列不整合。
- Benchmark leakage：Training／Tuning Dataへの評価問題・解答の混入。
- Synthetic contamination：Model生成Dataの反復利用による誤り・Bias増幅。
- Feedback contamination：評価者の好み、立場またはBiasをTruthと誤認する問題。
- Poisoning：意図的な悪性Data、Backdoor、誘導または不正混入。
- Provenance loss：Source、加工、Label主体、Reviewおよび利用履歴の消失。

次の状態を同義にしない。

```text
Data Exists
!= Trusted
!= Clean
!= Label Correct
!= Training Eligible
!= Evaluation Eligible
!= Production Eligible
```

`Bad Data`と`Incorrect Data`も同義にしない。事実として正しくても目的、Bias、Provenance、Label GuidelineまたはBenchmark分離に適合しなければ不適格になり得る。一方、有害・誤答・攻撃的なDataでも、Safety研究、Failure再現またはRepair評価では必要なEvidenceになり得るため、意味だけで自動削除しない。

Label Governanceでは単純多数決をTruthとしない。少なくとも次を追跡候補とする。

- Label Definition／Guideline Version。
- Annotator Identity Class、QualificationおよびConflict of Interest境界。
- Annotator別Label、Confidence、Disagreement Rateおよび理由。
- Source Context、Task PurposeおよびEvidence。
- Review／Adjudication履歴、判定者、Revisionおよび再Open Trigger。
- Training、Evaluation、Safety ResearchおよびProduction別Eligibility。

Phase 10以降の実装候補として、Dataset Registry、Data／Label Evidence、Transformation Lineage、Eligibility Policy、Adjudication Workflow、Benchmark IsolationおよびPoisoning／Leakage検査を検討する。

Phase 7では、これらを完全実装した、またはData Qualityが保証されたと主張しない。将来の再分類を可能にする最小Identity／Provenance／Consent／Export境界だけを保持する。

## 8. Phase 10以降へ延期する提携／License Data

Phase 10以降では、OSS利用企業または研究組織が独自のLicensed Dataset／契約Archive／Internal Knowledge Sourceを接続できるExtensionを再検討する。

再開時には少なくとも次をGateとする。

- 契約主体、利用許諾、地域、Retention、再配布、Training利用および派生成果物の権利。
- Tenant／Organization／User Scopeの分離。
- Credential、Billing、Rate Limit、監査および失効。
- Dataset Provenance、Version、更新、削除要求およびLicense終了時の撤去。
- Public OSS Coreと企業固有Adapter／Dataを分離するPackage境界。

提携／License Dataがなくても、Phase 7〜9のMARGPA Core、Local RAG、Public Web RetrievalおよびData Governanceは成立する構造にする。

## 9. Authority／非開始宣言

本書はScope／時期／既定値の予約であり、Phase 7開始、Network Access、Provider選定、Package導入、Credential作成、外部契約、Training、Source変更またはGit操作を現在許可しない。

Phase 7 READY後、Requirements／Architecture／ADR／Execution Plan／Acceptance Matrix／Exact Handoffへ再導出し、現行のPhase 6 Bugおよび未成立Acceptanceを隠さずEntry Gateを判定する。

## 10. Related Documents

- `docs/public/roadmap_ja.md` — Phase 7 RAG and Data Governance。
- `docs/project/shared/history/planned_work/phase_9_closure_public_technology_selection_reservation_ja_20260823163417.md` — Phase 7 Web Retrieval／Technology Decision Ledger予約。
- `docs/project/shared/history/planned_work/phase_7_phase_9_phase_10_closure_ready_sequence_correction_ja_20260823192316.md` — Phase 7 READY以降の順序予約。
- `docs/project/shared/history/planned_work/phase_6_interim_and_phase_9_final_roadmap_summary_reader_facing_requirements_ja_20260823185543.md` — Phase 7 Public Summary要件。
- U.S. Copyright Office, Circular 33 — Names／Titles／Short PhrasesとCopyrightの一般的説明。

## 11. 2026-08-29 Settings Web検索Control追記予約

Phase 7でWeb検索機能を実装する際、通常Settingsの「設定」画面へWeb検索の`OFF／ON` Controlを追加する。

配置は、**要約ModeおよびRAG設定が置かれている列**とし、要約Modeより上、すなわち当該列の最上段へ置く。Advanced Modeだけに閉じたControlにはしない。

```text
設定
  Web検索              OFF | ON   # 当該列の最上段
  要約Mode             ...
  RAG設定              ...
```

初期値は`OFF`とする。`OFF`の間はWeb検索、Query送信、Web取得および外部Network Callを実行せず、ModelがWeb検索を実行したかのような表示やClaimも行わない。

この`OFF／ON`はユーザー向けの検索機能有効化Controlである。既に予約済みのManual／Automatic起動方式、Web Evidence Governanceの`OFF／OBSERVE／ENFORCE`、Provider、Query／Context送信範囲およびData Controlsとは責務を混同せず、Phase 7 Exact Designで整合させる。

本追記はUser Decisionに基づくUI／Default予約であり、現時点のWeb検索実装、Network AccessまたはProvider利用を許可しない。

### 11.1 Control形式の補足

Web検索の`OFF／ON` Controlは独自のDropdown、Checkboxまたは別形式Buttonを新設せず、**同じ列にある要約ModeおよびRAG設定と同一のToggle切替Button／Component**を使用する。配置、寸法、選択状態、操作感およびVisual Styleも既存2 Controlと揃え、Web検索だけ異なるUI表現にしない。
