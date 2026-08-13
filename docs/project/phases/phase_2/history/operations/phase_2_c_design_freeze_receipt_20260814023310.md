# Phase 2-C Design Freeze Receipt

```yaml
receipt_id: phase_2_c_design_freeze_20260814023310
status: accepted
phase: phase_2
subphase: phase_2_c
created_at: 2026-08-14 02:33:10 JST
from_role: Phase 2設計担当者役
reviewed_by: プロジェクト責任者兼設計統括者役
to_role: Phase 2実装者役
```

## 1. Accepted Package

- `requirements/phase_2_c_persistent_conversation_api_ux_requirements_ja.md`
- `architecture/phase_2_c_persistent_conversation_api_ux_architecture_ja.md`
- `adr/phase_2_c_persistent_conversation_api_ux_adr_ja.md`
- `handoffs/phase_2_c_implementation_handoff_ja.md`
- `operations/phase_2_c_acceptance_matrix_ja.md`

## 2. Controller Review

- Persistent APIは`/api/v2/conversations/**`としてExisting v1から分離されている。
- BindingはLocal／Loopback／Auth disabled／Explicit opt-inの交差だけで成立する。
- Public Demo／Shared Basic Preview／Non-loopbackはPersistent Build／Read／Write 0である。
- Server Repositoryを唯一のCanonical Sourceとし、Client Full History、ScopeまたはPathをMutation Requestへ含めない。
- Retry／Regenerate／BranchはSourceを上書きしないCAS Mutationである。
- Terminal SSEはDurable Commit後、Conflictは409／Mutation 0／Detail再Readへ収束する。
- Browser StorageへConversation本文を永続化しない。
- Phase 2-DのConfig Control／Research Developer Modeを先取りしていない。
- Allowed／Forbidden Paths、Tests、RollbackおよびImplementer→Designer返却経路がExactである。

## 3. Authority

Phase 2実装者役は、Accepted HandoffのAllowed Paths内に限りPhase 2-Cを実装・Test・局所修正できる。Authorized Project Root外、Git、Network、External、Secret、Existing v1 Contract、Phase 2-A Domain／Port、Public／Basic PersistenceまたはConfig ControlへのAuthorityは発生しない。

## 4. Restart Point

```text
Last accepted subphase : Phase 2-B
Current work           : Phase 2-C implementation
Write lease            : Phase 2実装者役
Return route           : Implementer -> Designer -> Controller
Git                    : terminal campaign checkpointまで未実施
```
