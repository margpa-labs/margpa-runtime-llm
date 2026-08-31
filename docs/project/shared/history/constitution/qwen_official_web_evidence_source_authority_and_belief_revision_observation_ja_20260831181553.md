# Qwen公式Web Evidenceによる訂正受容／Belief Revision変化――Constitution／Judge研究Source Evidence

```yaml
document_id: qwen_official_web_evidence_source_authority_and_belief_revision_observation_20260831181553
document_type: constitution_judge_evidence_research_source
document_state: append_only_candidate
normative: false
language: ja
recorded_at: 2026-08-31 18:15:53 JST
decision_authority: user
phase: phase_8
model_family_observed: Qwen
observation_surface: real_browser_real_model_real_public_web_evidence
target_research:
  - runtime_constitution
  - semantic_governance
  - judge_and_repair
  - evidence_authority_and_provenance
causal_claim: not_established
```

## 1. Abstract

Phase 8のManual URL実画面確認中、同じUser訂正でも、User発言だけを与えた場合と、公式Web Evidenceを取得した後では、
Qwenの訂正受容と誤ったPriorの更新に明確なBehavior差が観測された。

観測の圧縮表現：

```text
User訂正のみ
-> 誤ったPriorを維持

公式Web Evidence＋User訂正
-> 読みを修正
-> 過去の訂正を受容
```

本観測は、Source Authority／ProvenanceがBelief Revision Successへ影響する可能性を示す。ただし、単一Model、単一Topic、
単一Conversation系列の実画面観測であり、因果関係、一般性または再現率を確定しない。

## 2. Evidence条件

### 2.1 公式Evidence取得前

Userは次の訂正を繰り返し与えた。

```text
Amane = あまね
天音かなた = あまね かなた
```

観測されたQwenの挙動：

- `天音かなた = てんおね かなた`という誤った読みを維持した。
- User訂正を受容せず、User側が誤っている可能性を示すPresentationを繰り返した。
- 会話内の訂正だけでは誤ったPriorの更新に成功しなかった。

### 2.2 公式Web Evidence取得

Phase 8 Manual URL機能で、Hololive公式Talent Pageを取得した。

```text
URL: https://hololive.hololivepro.com/talents/amane-kanata/
Title: 【卒業生】 天音かなた | 所属タレント一覧 | hololive（ホロライブ）公式サイト
Evidence内の表記:
- 天音かなた
- Amane Kanata
```

Web Evidenceは`Public Web`、Canonical URL、Fetched At、Content Type、Transformation、Digestおよび
`Untrusted External Content` LabelとともにCurrent Turnへ注入された。Runtime表示上のSource Authorityは`general`であり、
システムが公式性を自動証明したわけではない。Userが取得先をHololive公式Pageとして選び、内容とURLを確認した。

### 2.3 公式Evidence取得後

UserはEvidenceと明示的Mappingを組み合わせた。

```text
公式ページでは「天音かなた / Amane Kanata」。Amane = あまね。
```

観測されたQwenの変化：

- `天音かなた = あまね かなた`へ回答を修正した。
- 以前のUser訂正が正しかったことを受容した。
- 関連する訂正も、Evidence取得前より受け入れられやすくなった。

## 3. Interpretation

最小限の観測主張は次である。

```text
同一系統のUser訂正だけでは誤ったPriorが持続した。
公式Page由来の外部Evidenceと明示的Mappingを同時に与えた後、訂正受容と回答修正が成立した。
```

ここからの研究仮説：

```text
Evidence Source／Provenance／Authority Signal
-> Correction Acceptance Probability
-> Belief Revision Success Rate
-> Repair Stability
```

Alternative Explanationも残す。

- 単なるConversation Context累積。
- 同じ訂正の反復回数。
- 英字表記`Amane Kanata`がToken上の補助Signalになった。
- Web EvidenceのAuthorityではなく、追加Context量またはPrompt位置の効果。
- Sampling揺らぎ。
- Userの明示的Mappingの書き方の差。

従って「公式Sourceなら必ずModelが正しく修正される」「Authority Labelが因果原因である」とは主張しない。

## 4. Constitution／Judge候補

### 4.1 Evidence Authorityを内容と分離する

Evidenceは本文だけでなく、少なくとも次を別Fieldとして扱う候補がある。

```yaml
source_class: public_web
requested_url: string
canonical_url: string
source_authority_claim: string
authority_claim_origin: runtime_or_user_or_registry
fetched_at: timestamp
content_digest: sha512
transformation: string
untrusted_external_content: true
```

`official`等のAuthority ClaimをURL文字列だけからHard-codeしない。Runtimeによる検証済みAuthority、User指定、Registry登録、
一般Public Webを区別する。

### 4.2 Judge Criterion候補

```text
user_correction_without_external_evidence
user_correction_with_general_web_evidence
user_correction_with_verified_official_source
current_evidence_contradicts_historical_assistant_claim
assistant_accepts_correction
assistant_rejects_correction
assistant_updates_answer
assistant_reverts_after_later_turn
```

Judgeは「最終回答が正しいか」だけでなく、訂正前Prior、Evidence、訂正受容、修正内容および後続Turnでの保持を相関する。

### 4.3 Runtime Constitution候補

ConstitutionはAuthority Signalを、Tool／Action Authorityの拡張に使わない。一方、Evidence選択、Confidence、Judge Weight、
Contradiction DetectionおよびRepair Priorityには利用可能な入力とする。

```text
Evidence Authority Weight
≠ Tool Authority
≠ Action Permission
≠ Untrusted Content解除
```

公式SourceであってもPrompt Injection、取得時改変、Site Compromiseまたは誤記の可能性があるため、Untrusted External Content境界を保つ。

## 5. 再現実験候補

1. 同一質問／同一Seed／同一Model Revisionで、Evidenceなし、User訂正のみ、一般Web、公式Webを比較する。
2. Source本文を同一にし、Authority Metadataだけを変える条件を設ける。
3. Authority Metadataを同一にし、本文中の明示Mappingだけを変える。
4. 初回受容だけでなく、複数Turn後の再質問でRevision保持率を測る。
5. Qwen、DeepSeek、将来のMain Model候補で比較する。
6. Judge／Repair ON／OFF、OBSERVE／ENFORCE候補で比較する。
7. `Correction Acceptance Rate`、`Belief Revision Success Rate`、`Reversion Rate`、`Unsupported Deference Rate`を記録する。

## 6. Normative State

本書はConstitutionの制定済みRuleではない。Phase 10の二種Constitution全Docs編纂およびPhase 9のSemantic Governance／Judge設計で、
一次Sourceとして再評価する。Provider固有の恒久特性へ一般化しない。
