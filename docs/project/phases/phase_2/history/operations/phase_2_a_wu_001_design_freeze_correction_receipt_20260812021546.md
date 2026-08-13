# P2-A-WU-001 Design Freeze Correction Receipt

```yaml
receipt_id: p2_a_wu_001_design_freeze_correction_receipt
status: correction_applied_and_verified
created_at: 2026-08-12 02:15:46 JST
supersedes_digest_set: phase_2_a_wu_001_design_freeze_receipt_20260812015152
```

## Reason

P2-A-WU-003の自己Reviewで、将来のBranch復元とScope Isolationに影響する三つの不変条件を追加強化した。

- Completed Turnが存在するConversationはHeadを必須とする。
- Retry／RegenerateのDerived元はTerminal Turnとし、元Turnと同じBranch Parentを維持する。
- Conversation PageはScopeを保持し、異Scope Summary混入を拒否する。

初回Freeze ReceiptはHistoryとして保持し、編集しない。本ReceiptのDigest Setを最終Freeze正本とする。

## Final Frozen Document Digests

```text
2496e1587d80e23d7fd33f997ee2f5c78b71d552732dd86d85b0650fbc164765c02852541857702ff6e2f706b36b0d720a4bf65c5cd20c464d72d13ddd01ad6b  requirements/phase_2_a_conversation_domain_requirements_ja.md
5c381dc2f69e45fe448faefe656d2866ec767fb7b5ef413c2b831918b5380319f97879b531fe6646c0933d79a6cdb875022cc92b3b6169c6e1163548867962b4  architecture/phase_2_a_conversation_domain_architecture_ja.md
e9bf5dd804142cab4e139eeef37d1c3195dbcf13cb3fa94a43072debc637296ac66d51134c9b4883d973c289618679733c072a6fa5f9b95fe07046e178f3cf3a  adr/phase_2_a_conversation_domain_adr_ja.md
66da5532cc0cc9d3b7942b5f48a2a05618aaea3cede9119f7c48399b0fa587e65ee4f5e00f9e8f9d83c37c47637b6c0b66524e47b622b6cd7509f5d557f89555  governance/phase_2_a_implementation_authorization_envelope_ja.md
b2a8b5e09e8ea8ad24da0453eac28f34cd1ca98b7b635c07a0caa9baa94dbc5a22d9962409a6b00d60071b49b93aec5df633530ad6ad99ee7233b4ac72914e7c  operations/phase_2_a_execution_plan_ja.md
d6b670c489e9a0f4a822dcb6b555beb60d87286455a4fb806a5a8bc787f4979f433ced9a1ee8362a8860f93f156fad65bb022cbf4f7fd0b0d074eccfcfb8a8bd  handoffs/phase_2_a_implementation_handoff_ja.md
```

Path prefix is `docs/project/phases/phase_2/`.

## Validation

```text
Target Test           : 49 passed
Conversation／Web     : 107 passed
Full Suite            : 479 passed／3 deselected
Ruff／Mypy            : PASS
Technical Blocker     : NONE
```
