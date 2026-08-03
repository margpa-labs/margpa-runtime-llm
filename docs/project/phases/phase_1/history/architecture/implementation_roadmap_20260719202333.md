# MARGPA Runtime LLM 実装Roadmap

```yaml
document_state: current
created_at: 2026-07-19 20:23:33 JST
supersedes: implementation_roadmap_20260719171836.md
```

## 1. Current Decision

Phase 1完了状態で一度公開する。公開前にLightning AI Studioを第二Runtime Environmentとして成立させ、以後の各PhaseをMac／Lightningの両方で検証可能にする。

## 2. Phase 1 State

```text
Phase 1-A Environment／Metal                 : Complete／Accepted
Phase 1-B Model Adapter／CLI                 : Complete／Accepted
Phase 1-C Platform／Acceleration Hook        : Complete／Accepted
Phase 1-D Configuration／Response Language   : Complete／Accepted
Phase 1-E Thinking Presentation              : Complete／Accepted
Phase 1 Acceptance Follow-up                 : Ready／Implementation Pending
Phase 1-F Lightning Cross-environment        : Accepted／Implementation Pending
Phase 1 Cross-environment Final Review       : Waiting
Phase 1 User Acceptance                      : Waiting
Phase 1 Backup                               : Not Triggered
Phase 1 Publication                          : Not Started
```

Top-Level Phase 1状態：`Implementation Reopened for Acceptance Follow-up and Phase 1-F`

## 3. Phase 1-F

### Mandatory

- Python 3.12／3.13 Support Range
- Mac 3.13.14 Regression
- Lightning 3.12.11 Setup
- Linux x86_64 Container Detection
- llama.cpp CUDA Detection
- Lightning CUDA Profile
- CUDA Native Build／Model Smoke
- Mac／Lightning Environment Evidence

### Preferred／Conditional

- Lightning CPU Profile
- CUDA Buildを利用したGPU未割当CPU実行
- 必要時のCPU Build Recipe

CPUが期限を大きく圧迫する場合、Evidence、Known Limitation、User Approvalを条件にCUDA必須Gateを先に完了できる。

## 4. Phase 1 Publication Sequence

```text
Acceptance Follow-up
  → Phase 1-F実装
  → Mac Regression
  → Lightning CUDA Native Verification
  → CPU Verificationまたは明示Disposition
  → User Manual／Public Docs
  → User Acceptance
  → Designer Completion Declaration
  → Phase 1 Backup
  → Secret／Model／Log除外確認
  → Git／GitHub公開（ユーザー別途許可）
```

## 5. Later Phases

Phase 2以降の機能順は前Roadmapを継承する。

- Phase 2: Conversation Application and Web UI
- Phase 3: Audit and Definition Infrastructure
- Phase 4: Main Runtime Governance
- Phase 5: Guardrail, Judge, Repair, Observability
- Phase 6: 旧External Linux Phaseを廃止し、Phase 1-F後のCross-environment強化枠へ変更予定
- Phase 7: RAG
- Phase 8: Agent and Tool Execution
- Phase 9: Experiment and Research Platform
- Phase 10: Expansion and Cloud Scale

正式な番号再整理はPhase 1公開後に行ってよい。現在はPhase 1-F完了を優先する。

## 6. Backup Gate

既存Dual Approval Gateを維持する。ただし対象Project StateへPhase 1-FとAcceptance Follow-upを含める。Macだけの旧User Test結果で、新しいCross-environment SnapshotのBackup Gateを成立させない。

## 7. Publication Boundary

- GitHub Source公開とLive Web URLを分離する。
- Model Binary、Secret、実会話Log、RAG資料を公開しない。
- Phase 1の公開主張はCLI Runtimeと検証済みPlatformへ限定する。
- CPUが未完了なら、CUDAのみNative Verifiedであることを明記する。

## 8. Current Next Action

1. 実装担当へAcceptance Follow-upとPhase 1-Fの開始許可を出す。
2. 実装担当がMac側の共有変更とTestを完了する。
3. Lightning側でSetup／CUDA Build／Native Testを行う。
4. 実装Status後、設計者がReviewとIndexを作成する。
