# Phase 6 Ninth Rework — Start Recovery

Timestamp: 2026-08-24 16:05:41 JST
Role: 設計者兼実装者役
State: `NINTH_REWORK_IN_PROGRESS`

## 1. Authority

```text
GOV-013 SHA-512:
3de776b45cc748e03c624c5c936ad8e0792f6663a4af0d6f9545fc8723dda332c3c31f445cf1d8d93e70d8e34a87ee00ec60bc307ef30dcce5637ab16e5b7f37

Ninth Exact Handoff SHA-512:
07bc124193f88af7e5227038484028086998339dd492040f38cbb60c3d68fe6b004a05e7532c75cb9c9e9c9d323fd0e5cae2d54e1cadbf50b95feb8f618e09fc
```

Mandatory Reading 4文書を全文読了。

## 2. Exact Scope

`P6-RW8-CODEX-001`のJudge Evidence Publish Ownership 1件だけを差分修正する。
EighthのLifecycle／Deadline／UI実装、Seventh Package A〜Gは保持する。

WorkerはJudge／Repair結果とEvidence内容をMemory上のTyped Pending Payloadへ格納し、
同期ENFORCEの外部Evidence PublishはCaller-owned Terminal Arbitrationのみが許可できる
構造へ変更する。

## 3. Task-owned Temporary Root

```text
/Users/Nazuna Research/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/.venv/.t/phase_6_ninth_rework_20260824160541/
├── pytest/
└── tmp/
```

全pytestにExact Project内`--basetemp`を使用する。

## 4. Boundary

```text
Ninth Cycle Root-outside Action     : 0
Phase 6 cumulative known Incidents  : 2 (historical, retained)
Provider Memory / User runtime_data : 0
Git / Network / Model Mutation      : 0
Phase 6 Closure / Phase 7 / Roadmap : 0
```
