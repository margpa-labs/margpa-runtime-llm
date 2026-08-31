# Phase 9 READY前後 Public Portfolio用Demo画像・非開示Roadmap要約別版 予約

```yaml
document_id: phase_9_ready_portfolio_demo_images_and_non_disclosing_roadmap_summary_variant_reservation_20260831
document_type: append_only_planned_work
document_state: planned_not_started
language: ja
recorded_at: 2026-08-31 JST
decision_authority: user
implementation_authority: false
public_docs_mutation_authority: false
git_authority: false
candidate_gate:
  - phase_9_ready
  - phase_9_bounded_phase_6_semantic_debt_rework_completed
exact_start_trigger: explicit_user_instruction_at_the_time
```

## 1. User Decision

就職活動用PortfolioとしてMARGPA Runtime LLMを第三者へ提示できるよう、次の二つのPublic Artifact更新を予約する。

1. 現行画面に基づく新しい`docs/public/demo_images_ja.md`相当のDemo画像集を作る。
2. 現行`docs/public/roadmap_summary_ja.md`をSource Baseとしつつ、Nazuna固有の独自性／新規性要素を意図的に一切開示しない、別PatternのRoadmap要約版を新規作成する。

現時点ではどちらも未着手である。作業開始時期はUserが別途指示する。

## 2. Candidate Timing

利用可能量とPhase進捗に応じ、次のいずれかの区切りを候補とする。

```text
Candidate A: Phase 9 READY成立時

Candidate B: Phase 9で再開する、Phase 6時点の未完了中心Debt
             （Selene／Qwen3Guard／GD Semantic／Judge／Repair等）
             が有界完成した区切り
```

Candidate A／Bは自動Triggerではない。実際の開始は、その時点の利用可能量、進捗、画面完成度およびUserの明示開始宣言で決める。

## 3. Demo Images Refresh

新しいDemo画像集では、作成時点のAs-built画面だけを使用する。

- 古い開発途中画面をCurrentであるかのように再利用しない。
- Chat、RAG／Citation、Web Evidence、Governance、Judge／Guard、Dev Agent、Settings等から、PortfolioでProjectの幅が伝わる画面を選ぶ。
- 未完成、Fixture限定、Preview、OFF固定またはDeferredの機能を、実運用完成済みと誤表示しない。
- Local Path、個人情報、Secret、Token、非公開識別子、Private Chat、不要な内部Debug情報を画像へ残さない。
- 必要に応じて画像の撮り直し、Crop、順序整理、Caption更新、古い画像のHistory退避を行う。
- Exact File名、画像枚数、Asset Path、旧版の扱いは開始Gateで決定する。

## 4. Non-disclosing Portfolio Roadmap Summary Variant

別Patternの要約版は、次の両立を目的とする。

```text
Portfolio Appeal
  人が短時間見ただけでも、一般的なLocal LLM UIとは異なる広がり、
  設計の深さ、段階的な研究開発および実装密度を感じられる。

Non-disclosure
  Nazuna固有の独自性／新規性、核心Algorithm、内部Protocol、
  未公開Governance構造、再現可能な設計Recipeは一切開示しない。
```

### 4.1 Source Boundary

- Source Baseは作成時点の`docs/public/roadmap_summary_ja.md`とする。
- Canonical Detailed Roadmapは引き続き`docs/public/roadmap_ja.md`であり、別Patternを新しい正本にしない。
- As-built Source、Phase Closure、Stable DocsおよびManual Evidenceと照合し、事実を捏造しない。
- 現行要約版を上書きするか、別Fileとして併存させるかは開始時に決める。初期Preferenceは比較可能な別Fileである。

### 4.2 Include候補

- Projectの目的を、一般的で理解可能な言葉で短く示す。
- Phase単位の積み上げ、Current State、実装済みCapabilityおよび次の到達点を示す。
- Component分離、Mode切替、Evidence、Local RAG、Web Evidence、Agent／Tool Foundation等は、公開済みの表層Capabilityとして説明できる。
- 実画面、Test、Manual Acceptance、Phase進行など、Portfolioとして検証可能な成果を重視する。
- 読者が「一般的なChat UIだけではない」と認識できる構成、情報設計、比較軸および視覚的Hierarchyを用いる。

### 4.3 Exclude必須

- Nazuna独自性／新規性を直接説明する文言。
- 独自Algorithm、内部Protocol、Rule構成、Conflict解決方式、Compilation方式、Provider切替の核心、Agent Governanceの再現Recipe。
- 未公開Research Assetの具体構造、命名の意味、競争優位を再現できる詳細。
- 「世界初」「最先端」「唯一」「完全自律」等、比較Evidenceなしの誇大Claim。
- 未成立機能、Future ScopeまたはFixtureをCurrent Production Capabilityに見せる表現。

## 5. Writing Target

狙うLineは、秘密を匂わせる煽り文句ではない。

```text
Bad:
  独自技術を隠していると強調する。
  抽象語だけで「すごそう」に見せる。
  未完成Capabilityを完成済みに見せる。

Target:
  実装済みの幅、Phase進行、画面、Evidence、設計上の整理から、
  読者が自然に「何か一般的なものと違う」「設計と実装が深そう」と感じる。
```

すなわち、独自性の説明ではなく、公開して安全な成果の選び方、情報密度、構成および実証済み範囲によって差を示す。

## 6. Acceptance候補

- Demo画像が作成時点のCurrent UIと一致する。
- 個人情報、Secret、Private Pathおよび非公開Chatが含まれない。
- 別Roadmap要約が現行要約と詳細Roadmapへ矛盾しない。
- Nazuna固有の独自性／新規性要素を明示・暗示する再現可能な技術説明がない。
- 一般読者または採用担当者が、短時間でProjectの目的、規模、進捗、実装範囲を把握できる。
- 誇大Claimなしでも、一般的なLocal Chat UIとの差が成果物の構成から伝わる。
- Current／Preview／Fixture／Deferred／Futureの境界が正直である。
- Canonical RoadmapとPortfolio用Derived Artifactの責務が混同されない。

## 7. Non-authorization

本書は予約だけを固定する。次を現時点で許可しない。

- `docs/public/demo_images_ja.md`または画像Assetの変更。
- `docs/public/roadmap_summary_ja.md`、`docs/public/roadmap_ja.md`または新しいPublic Roadmap Fileの作成・変更。
- Screenshot取得、画像加工、公開、Git、CommitまたはPush。
- 候補Gate到達だけを根拠とする自動着手。

Userが時期を指定し、「やる」と明示した後に、当時点のAs-builtと公開境界を再確認して開始する。

## 8. User Addendum — Abstraction Boundary and Technology Selection

本節は2026-08-31のUser追記決定であり、第4節までの公開方針をさらに厳格化する。

### 8.1 Portfolio用Roadmap別版の追加非開示境界

- `OFF／OBSERVE／ENFORCE`という名称、三段階Mode、比較構造またはそれを連想させる説明を一切書かない。
- 特定の内部Governance構造、評価段階、適用段階、Authority構造または独自設計の発想へ読者を誘導しない。
- 各項目はかなり抽象化し、Projectが扱う領域、実装済みの一般Capability、進捗および利用イメージが分かる概要Levelに留める。
- 記載粒度は現行`docs/public/roadmap_summary_ja.md`程度を上限目安とする。ただし、同Fileに現在含まれる独自性／新規性へ繋がる表現をそのまま転記してよい、という意味ではない。
- Python、React、FastAPI、SQLite、RAG、Local LLM、Web UI、Test、REST API等、既存の一般的に使用されている技術および一般名称は通常どおり記載できる。
- 一般技術を組み合わせる具体的な独自Recipe、内部順序、判定条件または再現可能なArchitecture説明は開示しない。

### 8.2 Technology Selection同時更新

Portfolio Artifact更新を実行する同じGateで、`docs/public/technology_selection_ja.md`もCurrent As-builtへ更新する。

その更新にも本書と同じ公開境界を適用する。

- 一般的な採用技術、Library、Runtime、Storage、Frontend／Backend構成、Local Model実行基盤および採用理由は記載できる。
- Nazuna固有の独自性／新規性、内部Governance方式、独自Algorithm／Protocol、再現可能な構成Recipeは記載しない。
- `OFF／OBSERVE／ENFORCE`、三段階Modeまたはそこから独自発想へ到達し得る比較構造は記載しない。
- Current／Candidate／Deferred／未採用を正直に区別し、未成立Capabilityを採用済みと捏造しない。
- Portfolio用Roadmap別版、Demo画像集およびTechnology Selectionの間で、公開範囲、用語、Current Stateおよび非開示境界を一致させる。

### 8.3 Updated Work Set

開始Gateで扱う予約Artifactは、次の三点Setとする。

```text
1. Current UIに基づく新Demo画像集
2. 非開示境界を適用したPortfolio用Roadmap要約別版
3. 同じ非開示境界でCurrent化したtechnology_selection_ja.md
```

本追記も予約条件の固定だけであり、Userの明示開始宣言前にPublic Docsを変更するAuthorityを与えない。
