# OpenAI AGENTS.md Context RoutingとMARGPA Portable Execution-state Reconstruction設計比較Evidence

```yaml
document_id: openai_agents_md_context_routing_and_margpa_portable_execution_state_reconstruction_architecture_comparison_evidence_20260909132014
document_type: external_reference_architecture_comparison_evidence
document_state: append_only_history
recorded_at: 2026-09-09 13:20:14 JST
source_checked_at: 2026-09-09 13:20 JST
language: ja
decision_authority: user
recorder_provider: Codex
scope:
  - openai_agent_context_management
  - agents_md_instruction_discovery
  - margpa_project_neutral_bootstrap
  - hybrid_execution_handoff
  - portable_autonomous_development_governance_package
  - preliminary_patentability_hypothesis
evidence_policy:
  official_source_fact: externally_cited
  project_architecture: repository_evidence_and_meeting_synthesis
  user_context: user_reported_not_externally_verified
  comparison: analytical_inference_not_external_fact
  patentability: hypothesis_only_prior_art_search_not_done
```

## 1. 記録目的

本書は、OpenAIが公開しているCodexのContext／Instruction Routing方式と、MARGPA Runtime LLMで形成中のProject-neutral Bootstrap、Role／Authority復旧、Hybrid HandoffおよびPortable Autonomous Development Governance Package（PADG Package）を比較した会議内容を、後続のPhase 10設計、Constitution編纂、Recovery検証および先行技術調査に利用できるEvidenceとして保存する。

会議では、次の問いから議論が始まった。

> OpenAIもAutomationと長期Context管理に苦戦し、現在は`AGENTS.md`をRouter／Mapとして必要な文書へ到達させる方式を採用している、という以前の整理は正しかったか。

結論は次のように分離する。

1. OpenAI公式資料から、Context管理が大規模Agent作業の重要課題であること、巨大な単一Instruction文書より短いMapと構造化Docsを使う設計、およびCodexが階層的に`AGENTS.md`を探索・結合する機構が確認された。
2. 「OpenAIもだいぶ苦戦中」は会議参加者による評価・要約であり、OpenAI自身の逐語的な自己評価ではない。
3. MARGPA案がOpenAI公開方式の「次の層」であるという表現は、両Architectureを比較したProject側の分析であり、外部機関による評価や総合優位性の証明ではない。
4. PADG Packageが特許対象になり得るという話は、技術的具体化後に先行特許調査を行う価値があるという仮説であり、特許性または権利化可能性の確定ではない。

## 2. 会議で確認されたOpenAI側の問題設定と公開方式

### 2.1 巨大な単一`AGENTS.md`からMap／Docs構造へ

会議内で参照されたOpenAI公式記事`Harness engineering: leveraging Codex in an agent-first world`について、次の内容が共有された。

- 大規模で複雑なAgent作業においてContext Managementは主要課題の一つである。
- すべてを一つの巨大な`AGENTS.md`へ集約する方式は、Context消費、重要事項の埋没、陳腐化、検証困難という問題を持った。
- 短い`AGENTS.md`を百科事典ではなくMap／Table of Contentsとして扱い、構造化された`docs/`をSystem of RecordとしてTaskに必要な情報へ到達させる方向へ移行した。
- 会議では公式記事中の規模感を「約100行程度のMap」と整理した。

引用元URL：

- OpenAI, Harness engineering: `https://openai.com/index/harness-engineering/`

上記URLと記事要約は会議内で引用されたSourceを保持したものである。本記録作成時には、後述する現行Codex公式Docsで`AGENTS.md`の階層探索機構を別途再確認した。

### 2.2 Codexの現行`AGENTS.md`探索機構

現行のOpenAI公式Codex Docsから、次を確認した。

- Codexは作業開始前に`AGENTS.md`系Instructionを読み込む。
- Global ScopeではCodex Homeの`AGENTS.override.md`を優先し、存在しなければ`AGENTS.md`を読む。
- Project ScopeではProject RootからCurrent Working Directoryまで降り、各階層でOverride、通常File、設定されたFallback名の順に候補を探す。
- Root側からCurrent Directory側の順で結合され、深い階層のInstructionが後段へ来る。
- 空Fileは無視され、合計Size上限がある。上限到達時にはInstructionをNested Directoryへ分割する案が公式Docsに示されている。
- Instruction ChainはRun／Session開始時に再構築され、現在Directory、Override、Fallback FilenameおよびSize上限を検証できる。

引用元URL：

- OpenAI Codex Docs, Custom instructions with AGENTS.md: `https://learn.chatgpt.com/docs/agent-configuration/agents-md`
- 同DocsへのDeveloper入口: `https://developers.openai.com/codex/guides/agents-md`
- OpenAI Developers documentation index: `https://developers.openai.com/llms.txt`

会議中に参照された、Codex Agent Loopの公開解説URLもSourceとして保持する。

- OpenAI, Unrolling the Codex agent loop: `https://openai.com/index/unrolling-the-codex-agent-loop/`

### 2.3 長期実行、CompactionおよびProgressive Disclosure

会議では、OpenAIの2026年時点のAgents／Harness関連資料に、configurable memory、progressive disclosure、`AGENTS.md`、filesystem tools等の構成要素が現れ、別の公開議論ではcontext switchingが次のbottleneckとして扱われている、という整理も共有された。

この部分は本記録作成時に該当記事の一意なURLを再特定できていないため、公式確認済みFactへ昇格しない。会議で提示された論点として保持し、Phase 10の正式比較時にSourceを再探索する。

一方、OpenAI公式Model Guidanceでは、長期AgentのCompaction時に、完了Action、Active Assumption、ID、Tool Outcome、未解決Blockerおよび次の具体Goalを保持するよう案内している。また大規模Tool CatalogではTool Searchで必要Subsetだけを遅延Loadする考えが示されている。

引用元URL：

- OpenAI Model Guidance: `https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.5`

## 3. OpenAI公開方式とMARGPA暫定方式の対応

会議では、OpenAI公開方式を次の最小形として捉えた。

```text
AGENTS.md
  → relevant docs
```

これに対し、MARGPA暫定方式は次の復旧Chainを目標としている。

```text
Bootstrap Index
  → Role / Authority / Recovery Baseline
  → Project Current-state Discovery
  → Provider-neutral Core
  → Provider Adapter
  → Exact Current Task Handoff
  → Evidence / Return / Recovery
```

この違いは「必要Docsを見つけやすくするIndex」だけではない。目標は、Context Loss、Compaction、Task再作成またはProvider変更後のAgentに対して、次を推測で補完せず再構成することである。

- 自分がどのRoleか。
- どのProject／Authorized Rootにいるか。
- 現在位置、Current PhaseおよびActive Handoffは何か。
- 何を読む必要があるか。
- 何をしてよいか、何をしてはいけないか。
- 今回のTaskで実行すべきWork Unitは何か。
- どのAcceptanceとEvidenceを満たして返すか。
- Stop／Resume時に何を保持し、次Taskへ何を渡すか。

会議で用いた機能分解は次のとおりである。

```text
Bootstrap Index
    = 長期・安定した意味空間

Project Discovery / Manifest
    = 現在いるProject世界の特定

Role View
    = 実行主体の役割と上限

Provider Adapter
    = 現ProviderのTool・Capability・制約への写像

Hybrid Handoff
    = 現時点のTask、Scope、順序、禁止、Acceptance Delta

Evidence / Return Contract
    = 実行した事実、未実行、失敗、最大Claim、次Action
```

## 4. Stable BaselineとCurrent Deltaの分離

会議で特に重要とされた分離は次である。

```text
Bootstrap Index
  → stable role / authority / recovery baseline

Hybrid Handoff
  → current task / work unit / scope / acceptance delta
```

この構造により、TaskごとにProject全履歴または全運用規則を再送するのではなく、Stable BaselineとCurrent Deltaだけを結合する。期待される効果は次である。

- Context消費の削減。
- Compaction後の復旧範囲の明確化。
- Task間Handoffの差分比較。
- Providerを替えた場合の同義Contract比較。
- 古い規則、Current HandoffおよびTask固有例外の混同低減。
- 復旧時に何が欠落したかの検査可能化。

## 5. Knowledge ReconstructionとAuthority Reconstructionの分離

MARGPA案の中心Invariantとして、次が確認された。

```text
Bootstrap / Recovery Readiness
  != Automatic Role Grant
  != Automatic Project Authority
  != Automatic Mutation Permission

Knowledge Reconstruction
  != Authority Reconstruction
```

文書を読んだこと、Role名を知ったこと、過去に同じRoleを担当したことまたは同じProviderであることは、現在TaskのAuthorityを自動生成しない。

Effective Authorityは概念上、少なくとも次の交差として再確定する。

```text
User Decision
∩ Target Project
∩ Authorized Root
∩ Active Handoff
∩ Role Ceiling
∩ Provider Capability
```

この分離は、一般的なMemory／Knowledge Retrievalで混ざりやすい「知っている」と「許可されている」を別Stateとして扱う。これはContext RecoveryだけでなくGovernance Architectureの問題である。

## 6. Current Position DiscoveryとConflict保持

Project-neutral Bootstrapは、特定Projectの`roadmap_ja.md`等をFile名で固定しない。Authorized Root内でRoadmap、Current Documentation Index、Active Phase、Stable、Current Handoff等に相当する候補を探索する。

復旧結果は少なくとも次を区別する。

```text
found_current
not_found
conflicting_candidates
history_or_archive_only
```

- 完全新規Projectで対象が存在しない場合は正常に`not_found`とし、存在を捏造しない。
- `history/`、ArchiveまたはBackupだけをCurrentとして扱わない。
- 複数のCurrent候補が矛盾する場合、Timestampだけで一件を選ばずConflictを保持する。
- Fluentな推測で「たぶんこのRoadmap」「おそらくこのRole」を作らない。

この設計は、復旧における状態捏造をArchitecture側で抑止するためのものである。

## 7. Hybrid Handoffと検証可能なExecution Contract

採用候補のHandoff形式は次である。

```text
Natural-language Intent / Rationale
  + XML or Markdown Section Boundary
  + JSON Execution Contract
```

自然言語は目的、背景、理由、例外の意味を保持する。XML／MarkdownはInstruction、Context、Evidence、Acceptance等の境界を分離する。JSONは比較すべき状態を固定する。

```json
{
  "task_count": 2,
  "create_new_task": false,
  "wait_mode": "complete_wait",
  "git": "deny"
}
```

JSON化の主価値は、LLMが必ず従うことではない。次を機械的に比較できることである。

```text
Expected Contract State
  vs
Observed Action / Trace
```

この差分を保持すれば、将来次へ拡張できる。

```text
handoff_v1.json
  → actual execution trace
  → contract violation detector
  → evidence / repair / regression
```

## 8. Architecture比較表

| 問題面 | OpenAI公開方式の基本回答 | MARGPA暫定案 |
|---|---|---|
| Context過多 | Mapから必要Docsへ到達 | 同じ問題を扱い、Stable BaselineとCurrent Deltaも分離 |
| Docs腐敗 | Structured Docs／System of Record | Stable＋History＋Freshness／Discovery Gate |
| 新Task復旧 | `AGENTS.md`／Docsを再読 | Role別BootstrapとCurrent Handoffで状態再構成 |
| Project差 | Repository階層に依存 | Project-neutral Core＋Manifest／Bounded Discovery |
| Provider差 | Codexの公式Instruction機構 | Provider-neutral Core＋Provider Adapter |
| Authority | Instructionの階層とOverride | ReadとAuthorityを分離しEffective Authorityを再計算 |
| Current位置 | Repository Docsから探索 | Current／Stable／Active、History／Archive、Not-found、Conflictを区別 |
| 矛盾 | Instruction／Navigation問題として処理 | Guess禁止、ConflictをEvidenceとして保持 |
| Task固有指示 | Prompt／Instruction | Hybrid Structured Execution Contract |
| Stop／Resume | Session／Context機構に依存する部分が残る | Stop／Resume／Handoffを明示Contract化 |
| Cross-provider | Codex単体Docsの直接対象外 | 同義Core ContractをProvider Adapterで比較 |
| 再現性 | HarnessとSession Log | Evidence、Exact Return、Maximum Claim、Recovery |

この比較は、公開資料から見える範囲とProject設計を比較した分析である。OpenAI内部の非公開Architecture全体との比較ではなく、MARGPAの総合優位を主張しない。

## 9. Phase 10正式化時の重要5項目

会議では、現暫定案をPhase 10で正式化する際に次の5項目を重視すると整理した。これらは既に別のPlanned Workへ予約済みである。

### 9.1 Bootstrap Index自体の腐敗検知

最低候補Field：

- `last_verified_at`
- Source Revision
- Digest
- Owner
- Coverage

### 9.2 Machine-checkable Coverage

最低必須カテゴリ：

- `authority`
- `role`
- `docs`
- `recovery`
- `evidence`
- `current_position`

Link切れ、欠落、重複、Current不明およびHistory誤参照を検査する。

### 9.3 Schema Validation

Hybrid Handoff JSONを正式なJSON Schemaへ固定し、少なくとも送信前に次を検出する。

- Duplicate Key
- Invalid Enum
- Required Field欠落
- ID／Scope不一致
- Forbidden／Required Actionの矛盾

### 9.4 Authorityに基づくConflict Precedence

新しいTimestampだけを勝者にしない。意味Authorityの例は次である。

```text
User Decision
> Accepted Correction / Addendum
> Active Handoff
> Stable Baseline
> Historical Record
```

Exact PrecedenceはPhase 10で既存Authority Matrixと統合して確定する。

### 9.5 Recovery Dry-run

新規Taskへ原則として次だけを渡す。

```text
Controller Bootstrap Index
Designer / Implementer Bootstrap Index
Current Handoff
```

余計なDocsを事前投入せず、Project位置、Role、Authority、Required Reading、禁止事項および次Actionを再構築できるかを検証する。成功すれば、Mapの存在ではなく実Recovery CapabilityをEvidence化できる。

関連予約：

- `docs/project/shared/planned_work/phase_10_project_neutral_controller_recovery_handoff_bootstrap_index_reservation_ja_20260909075701.md`
- `docs/project/shared/planned_work/phase_10_bootstrap_integrity_schema_authority_and_recovery_dry_run_reservation_ja_20260909122852.md`

## 10. MARGPA案の独自性候補として整理された範囲

会議では、MARGPA案を次のように要約した。

> 長期Contextそのものを移送するのではなく、Canonical情報、Role制約、Authority情報、Current StateおよびCurrent Task Deltaから、許可されたAgent実行状態を再構築する。

仮称の技術単位：

```text
Project-neutral Portable Agent Execution Environment

1. Bootstrap IndexからRole / Authority / Recovery Baselineを復元
2. Authorized Root内だけでCurrent Project StateをBounded Discovery
3. User Decision、Active Handoff、Role Ceiling、Provider Capability等からEffective Authorityを再構築 destination
4. Provider-neutral CoreをProvider Adapterで実Taskへ写像
5. Stable BaselineとCurrent Deltaを分離
6. Current DeltaをStructured Execution Contractとして渡す
7. Stop / Resume / Return / Evidenceを同じContract体系で保持
8. Context Loss / Task Recreation / Provider Switching後にも実行状態を再現
```

ここで比較上の短い表現は次となる。

```text
OpenAI公開方式の中心:
  Agentを必要なContextへ到達させるKnowledge Navigation

MARGPA暫定案の拡張目標:
  Knowledge Navigation
  + Identity Recovery
  + Authority Reconstruction
  + State Discovery
  + Execution Contract
  + Cross-provider Portability
  + Evidence-based Recovery
```

これはProject側のArchitecture Hypothesisである。OpenAIの非公開機能に同等構成が存在しないこと、既存製品／論文／特許に先行例がないこと、またはMARGPAが総合的に優れることは未証明である。

## 11. Failureを研究資産へ変換するR&D Pattern

会議では、MARGPA案がOpenAI資料を模倣して生まれたのではなく、Codex、Claude、Copilot等との実運用で起きたContext Loss、Authority逸脱、誤った再開、自然言語Instructionの脱落、Quota／時間消費等を分解して形成された点が重要視された。

```text
Operational Incident
  → Observation / Evidence
  → Failure Surface decomposition
  → Generalized Invariant
  → Architecture / Constitution
  → Regression Test
  → Portable Governance Asset
```

会議中の比喩的・ユーモラスな表現は、Providerの失敗を非難だけで終わらせず、一滴も捨てずにEvidence、Rule、RegressionおよびPortable Packageへ変換するという研究姿勢を示していた。

後からOpenAI公開資料と同じ問題面が確認されたことは、MARGPAの問題設定が現実のAgent Engineering課題と重なる状況証拠になる。ただし、独立発見そのもの、発明者性、先使用または新規性を法的に証明するものではない。

## 12. Resource Context

会議では、MARGPA設計が組織的R&D予算を持つ大規模Teamではなく、生成AI利用歴が比較的浅い個人によって、強い金銭、Hardware、Quota、時間および睡眠制約下で進められているという対比も明示された。

これはUser報告に基づくProject Contextであり、外部監査済みの財務情報ではない。技術Claimの証明には使わない。一方、次の設計要件を説明するResource Evidenceとして意味を持つ。

- 全Docsを毎回読ませない。
- Stable BaselineとDeltaを分離する。
- 不要なTask、Retry、PollingおよびReview Loopを抑止する。
- Model／Provider変更後の再作業を減らす。
- Quotaと人間のManual負担をArchitecture上のResourceとして扱う。

会議中の「研究能力と現在のResource Allocationが一致していない」という表現、および開発継続に必要な資源確保を研究炉心への燃料接続になぞらえた表現は、このResource制約と技術規模の不均衡を示す評価であり、客観的な能力ランキングではない。

## 13. 特許候補としての整理

### 13.1 正式名称

会議中に一時名称が曖昧だったが、Project内の正式予約名は次である。

```text
Portable Autonomous Development Governance Package
Short name: PADG Package
```

関連予約：

- `docs/project/shared/history/planned_work/phase_10_ready_portable_autonomous_development_governance_package_two_pass_compilation_reservation_ja_20260828091200.md`

### 13.2 特許の芯候補

会議で挙げられた芯候補は次である。

> 異なるLLM Agent、ProviderまたはProject間で長期Contextそのものを移送せず、参照可能なCanonical情報、Role制約、Authority情報、Current StateおよびTask Deltaから、許可された実行状態を再構築する方式。

補助候補：

- Bootstrap ReadinessとAuthority Grantの分離。
- Project StateのBounded Discoveryと`not_found`／`conflict`保持。
- Provider-neutral CoreとProvider Adapter。
- Stable BaselineとCurrent Deltaの分離。
- Structured ContractとObserved TraceのViolation検出。
- Stop／Resume／Return／Evidenceの同一Contract体系。
- Context Loss、Task Recreation、Provider Switching後の再現。

### 13.3 JPO公式資料から確認できる範囲

JPO審査基準では、ソフトウェアによる情報処理がハードウェア資源を用いて具体的に実現される場合、発明該当性の検討対象になり得ることが示されている。コンピュータソフトウェア関連発明は、単に「ソフトウェア」「コンピュータ」と記載するだけでなく、用途に応じた具体的な情報処理とハードウェア資源の協働が重要となる。

引用元URL：

- JPO 特許・実用新案審査基準 第III部 第1章: `https://www.jpo.go.jp/system/laws/rule/guideline/patent/tukujitu_kijun/ht/03_0100.html`
- JPO 特許・実用新案審査ハンドブック: `https://www.jpo.go.jp/system/laws/rule/guideline/patent/handbook_shinsa/`
- JPO AI関連技術に関する特許審査の事例: `https://www.jpo.go.jp/system/laws/rule/guideline/patent/ai_jirei.html`
- JPO Recent Trends in AI-related Inventions（2026）: `https://www.jpo.go.jp/e/system/patent/gaiyo/ai/ai_shutsugan_chosa.html`

本記録時点でJPOの審査基準改訂案内は2026-06-25更新、AI関連技術事例Pageは2026年更新分が公開されていることを確認した。

### 13.4 未確認事項と停止線

次は未実施である。

- OpenAI、Anthropic、Microsoft、Google、IBM、Agent系企業等の先行特許調査。
- 論文、OSS、製品および標準仕様の網羅調査。
- Claim Chart作成。
- 発明の新規性／進歩性／発明該当性の法的評価。
- 発明者、公開日、秘密管理および出願Timingの整理。
- 弁理士によるReview。

したがって現在の正確な結論は次である。

```text
Patent granted / patentable
  = NOT ESTABLISHED

Concrete patent candidate worth prior-art research
  = YES, preliminary hypothesis
```

完成後の候補手順：

```text
Working implementation
→ Architecture freeze
→ Failure / Improvement comparative evidence
→ Claim-level prior-art search
→ Patent counsel review
→ Filing / publication decision
```

本書は法律助言ではなく、出願可能性を保証しない。

## 14. Evidence分類

| Claim | 分類 | 状態 |
|---|---|---|
| CodexがGlobal／Project階層の`AGENTS.md`を探索・結合する | OpenAI公式Docs | CONFIRMED |
| 巨大`AGENTS.md`より短いMap＋Structured Docsを使うというOpenAI記事要約 | 会議で引用されたOpenAI公式記事 | SOURCE URL RETAINED |
| Context Managementを重要課題として扱う | OpenAI記事の会議内要約 | SOURCE URL RETAINED |
| 「OpenAIもだいぶ苦戦中」 | 会議参加者の評価 | INFERENCE |
| MARGPAはRole／Authority／Current State／Provider／Task Deltaまで再構成対象にする | Project設計・Repository Evidence | CONFIRMED DESIGN INTENT |
| MARGPA案はOpenAI公開方式の次の層を扱う | Architecture比較 | INFERENCE |
| MARGPAがOpenAI Agent基盤より総合的に優れる | 比較Evidenceなし | NOT CLAIMED |
| PADG Packageに特許候補となる技術単位がある | Preliminary technical hypothesis | CANDIDATE |
| PADG Packageが実際に特許を取得できる | 先行技術・法的評価未実施 | NOT ESTABLISHED |
| 個人・資源制約下で設計が進んでいる | User-reported Project Context | REPORTED, NOT EXTERNALLY VERIFIED |

## 15. 現時点の再利用先

- Phase 10 Docs統合とPADG Package編纂。
- Project-neutral Controller／Designer-Implementer Bootstrap正式化。
- Hybrid Handoff JSON Schema。
- Authority ReconstructionとConflict Precedence。
- Recovery Dry-runとCoverage検査。
- ConstitutionのContext Recovery、Authority、Evidence、Resource Rule。
- Provider間Recovery比較。
- 特許／先行技術調査のQuestion List。

関連する現行Project文書：

- `docs/project/shared/history/automation/development_agent_hybrid_handoff_and_provider_neutral_role_bootstrap_decision_evidence_ja_20260909083759.md`
- `docs/project/shared/task_roles/development_agent_hybrid_structured_instruction_handoff_operating_rule_ja.md`
- `docs/project/shared/operations/cross_project_development_governance_constitution_plan_ja.md`
- `docs/project/shared/planned_work/phase_10_project_neutral_controller_recovery_handoff_bootstrap_index_reservation_ja_20260909075701.md`
- `docs/project/shared/planned_work/phase_10_bootstrap_integrity_schema_authority_and_recovery_dry_run_reservation_ja_20260909122852.md`

## 16. Source Register

確認／記録日: 2026-09-09 JST

### OpenAI

1. Harness engineering: `https://openai.com/index/harness-engineering/`
2. Unrolling the Codex agent loop: `https://openai.com/index/unrolling-the-codex-agent-loop/`
3. Custom instructions with AGENTS.md: `https://learn.chatgpt.com/docs/agent-configuration/agents-md`
4. Developer入口: `https://developers.openai.com/codex/guides/agents-md`
5. OpenAI Developers index: `https://developers.openai.com/llms.txt`
6. OpenAI Model Guidance: `https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.5`

### Japan Patent Office

1. 発明該当性及び産業上の利用可能性: `https://www.jpo.go.jp/system/laws/rule/guideline/patent/tukujitu_kijun/ht/03_0100.html`
2. 特許・実用新案審査ハンドブック: `https://www.jpo.go.jp/system/laws/rule/guideline/patent/handbook_shinsa/`
3. AI関連技術に関する特許審査の事例: `https://www.jpo.go.jp/system/laws/rule/guideline/patent/ai_jirei.html`
4. Recent Trends in AI-related Inventions: `https://www.jpo.go.jp/e/system/patent/gaiyo/ai/ai_shutsugan_chosa.html`

## 17. 非Authority宣言

本書はAppend-only History Evidenceである。次を自動的に許可または成立させない。

- Phase 10開始。
- PADG Package実装または公開。
- Bootstrap／Handoff Schemaの変更。
- 外部調査、出願、公開または弁理士依頼。
- OpenAI方式に対する優位性Claim。
- Patentability Claim。
- Active Handoff、Stable RuleまたはUser Decisionの置換。

## 18. 作成時表記訂正（Append-only）

§10の番号3末尾に混入した`destination`は意味を持たない編集上の残留文字列である。該当行は次の意味として読む。

```text
3. User Decision、Active Handoff、Role Ceiling、Provider Capability等からEffective Authorityを再構築
```
