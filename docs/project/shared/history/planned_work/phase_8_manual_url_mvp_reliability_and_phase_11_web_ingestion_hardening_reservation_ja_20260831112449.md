---
document_id: phase_8_manual_url_mvp_reliability_and_phase_11_web_ingestion_hardening_reservation_20260831112449
document_type: append_only_planned_work_scope_refinement
document_state: current_decision_reserved_not_started
language: ja
recorded_at: 2026-08-31 11:24:49 JST
decision_authority: user
authority_owner: Nazuna Research
source_manual_evidence: ../../../phases/phase_8/history/operations/phase_8_user_mac_manual_acceptance_web_segment_1_evidence_ja_20260831112449.md
source_finding: ../../../phases/phase_8/history/operations/phase_8_manual_web_direct_url_reliability_grounding_and_context_budget_findings_ja_20260831112449.md
implementation_authorized: false
network_authorized: false
---

# Phase 8 Manual URL MVP Reliability／Phase 11 Web Ingestion Hardening予約

## 1. User Decision

Phase 8実画面で、Manual URL機能について次を確認した。

- `example.org`はFetch、Chat Evidence、Citation、Reload／Restartまで成立した。
- Loopbackは`private_or_loopback_address`で拒否された。
- 大きなWordPress PageはRaw HTML全体の注入によりContext上限を超過した。
- 別の通常Public URLは取得できず、Chat側は`url_rejected`だけを表示した。
- 取得失敗後もModelが非Grounded回答を生成した。

Userは、表示だけでなく「普通の公開Page情報を安定してModelが取得できない」ことを中心問題と明示した。

## 2. Phase 8へ戻すBounded Scope

```text
- Transient DNS／Connect FailureのBounded Retry。
- Public IPv4／IPv6 Candidateの安全な有界Fallback。
- Aggregate／Specific Failure ReasonのLive／Persistence／UI保持。
- Evidence-only Fetch失敗時の非Grounded Model回答禁止。
- Loopback／Private／Metadata／Dangerous Port拒否の維持。
```

この範囲はManual URL MVPの中心成立に必要な小〜中規模Reworkとして扱う。

## 3. Phase 11以降へ残すScope

```text
- Full HTML Normalizer／Readable Content Extractor。
- Script／Style／Boilerplate除去とSource別Parser。
- Chunking／Ranking／Contradiction／Budgeted Multi-source Injection。
- General Search Provider／Automatic Search。
- Browser Rendering／JavaScript／Anti-bot／Login Site。
- Hostile-site、Poisoning、PDF／Archive／Media Parser Isolation。
- DNS Pinning／Rebinding耐性を含むProduction Hardening。
```

ただしPhase 8のBounded Reworkで簡易ExtractorまたはEvidence Hard Capを追加する余地は残す。Current Contextへ収まらないRaw HTMLを
そのまま注入してOpaque Context Failureを起こす状態は、少なくともTyped Failureへ収束させる。

## 4. UI予約

Current実装は専用Manual URL欄を使う。Userが想定した最終UXは、通常Message入力へURLを貼り、そのTurnで明示的に取得・参照する方式。
この差はPhase 8 Reliability Fixから分離し、Phase 10の右Panel／Citation UIまたはPhase 11 Web Runtimeで再設計する。

## 5. Claim Boundary

Phase 8でClaimできる最大範囲は、User明示URLを有界・安全・正直に取得し、成功EvidenceだけをCurrent Turnへ渡すManual MVPである。
General Web Search、任意Site安定取得、Browser相当の閲覧能力またはSource品質保証をClaimしない。

本書は予約であり、実装、Network、Git、Phase 8 ClosureまたはPhase 9開始Authorityを与えない。
