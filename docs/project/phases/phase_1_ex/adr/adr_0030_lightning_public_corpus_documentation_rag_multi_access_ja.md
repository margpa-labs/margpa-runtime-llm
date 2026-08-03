# ADR-0030: Lightning Public Corpus Documentation RAG Multi-access

```yaml
document_id: adr_0030_lightning_public_corpus_documentation_rag_multi_access
status: accepted
language: ja
created_at: 2026-08-01 09:10:03 JST
accepted_at: 2026-08-01 09:10:03 JST
owner: 設計統括者役
phase: phase_1_ex
implementation_authorized: true_with_accepted_handoff
supersedes:
  - adr_0029_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook
supersedes_in_part:
  - adr_0027_public_demo_minimal_access_and_deferred_control_hooks
extends:
  - adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook
```

## 1. Context

ADR-0029では、Lightning Basic Previewだけが公開8文書をRAG利用し、Public DemoはRAGを強制拒否する設計を採用した。

その後、ユーザーから次が確定した。

- Lightningへ配置する8文書は、現在Project内のMac RAG Corpusとは内容が異なる外部公開用文書である。
- 8文書は誰に閲覧されても問題ない。
- Basic認証Previewと認証なしPublic Demoの両方で、同じ8文書をRAG利用可能にする。
- Lightning Platform上の操作は、引き続きユーザーが行う。
- 手動Hit Keyword表／Model参照Index表はHard-codeと保守性の問題があるため、現時点で採用しない。

## 2. Decision

Basic PreviewとPublic Demoの両方をDocumentation RAG `eligible`とし、同一のExplicit Public 8-file Corpus Feature Profileを利用可能にする。

```text
basic_preview:
  authentication = basic
  documentation_rag = eligible

public_demo:
  authentication = none
  documentation_rag = eligible

shared Lightning corpus:
  exact public 8 files only
```

AuthenticationとRAG Capabilityを独立させる。

## 3. Corpus Decision

Lightning RAG Corpusは次だけとする。

```text
docs/public/overview_ja.md
docs/public/overview_en.md
docs/public/concept_ja.md
docs/public/concept_en.md
docs/public/roadmap_ja.md
docs/public/roadmap_en.md
docs/public/technology_selection_ja.md
docs/public/technology_selection_en.md
```

`docs/project/**`、History、Lossless、Allowlist外Public MarkdownおよびProject Root外Pathを含めない。

## 4. Access／Security Decision

Public DemoへRAGを許可しても、次を許可しない。

- Internal Docs参照。
- Corpus切替。
- Profile Path指定。
- Tool／Agent／External I/O。
- Prompt／回答／Thinking／Corpus本文の永続保存。
- Document内容からのAuthority生成。

Public DemoはCredentialを引き続き継承しない。RAG Profileは公開Corpus Configであり、Credentialとは別に検証して渡す。

## 5. Technology Decision

既存Sparse RAG Coreを再利用する。

```text
Source:
  explicit project-root-bounded Markdown files

Chunk／Index／Retrieve／Assemble／Cite:
  existing deterministic adapters

Index:
  in-memory／lazy／non-persistent

New Dependency:
  none

Additional Model:
  none
```

## 6. Retrieval Guidance Decision

文書別Hit Keyword列、Model参照用Index表またはProject固有Subject Mappingを実装しない。

これらは検索精度を上げる可能性がある一方、Hard-code、Stale Mapping、多言語同期、未知文書対応および保守コストの問題を持つ。

将来のRAG精度再設計時に、自動抽出、Build-time生成、Semantic／Hybrid Retrieval、Query Decomposition、Governance／Judge／RepairおよびModel交換を比較して改めて判断する。

## 7. Defaults

Basic PreviewとPublic DemoのProject Docs設定はDefault OFFとする。

```text
OFF:
  no corpus scan／no index build／no retrieval

ON:
  public 8-file adapter only
```

## 8. Lifecycle Decision

Basic PreviewのBasic認証／Stateful Lifecycleと、Public Demoの認証なし／Stateless Lifecycleを維持する。

両方のForeground `run`へ同じ検証済みRAG Profileを渡す。Traffic-aware Wake後は最初のRAG ON RequestでIndexを再構築する。

## 9. Platform Authority

Repository実装者は次を操作しない。

- Lightning Studio。
- API Builder。
- URL／Port。
- Managed Secrets。
- Private Bootstrap。
- Sleep／Wake。
- Machine／Credit。

配置、起動、停止およびManual Acceptanceはユーザーが行う。

## 10. Consequences

### Positive

- 認証の有無にかかわらず、公開可能DocsについてProject自身が説明できる。
- Basic／Publicで同一Corpus Contractを再利用できる。
- 内部DocsをLightningへ持ち込まずに済む。
- Mac／Lightning／将来CloudでAdapter交換性を実証できる。

### Risk／Cost

- 匿名利用者もRAG Cold Buildを発生させられる。
- Citation付き誤回答は残り得る。
- JA／EN重複がRankingへ影響し得る。
- Access Profile、ScriptおよびTestの変更が必要になる。

公開8文書のLexical Indexは追加Model推論を使用せず、小規模In-memory処理である。現時点ではこのRiskを受容する。

## 11. Superseded Scope

ADR-0029の次をSupersedeする。

```text
Public Demo:
  RAG denied
  adapter construction zero
  docs scan zero
```

ADR-0027のPublic RAG強制無効DecisionをSupersedeする。

維持する項目：

- Basic PreviewとPublic DemoのAccess分離。
- Public Demoの明示Profile。
- Public専用Control Hookは現在OFF。
- Credential非継承。
- Prompt／回答の非永続。
- Platform操作のユーザーAuthority。
- Model／Deployment交換性。

## 12. Acceptance

本ADRをAcceptedとし、後継Requirements、Architectureおよび実装担当Handoffの範囲でRepository実装を許可する。

Lightning実機Acceptanceはユーザー手動Test後に別Reviewで判定する。
