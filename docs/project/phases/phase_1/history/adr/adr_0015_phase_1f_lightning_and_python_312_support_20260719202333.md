# ADR-0015: Lightning対応をPhase 1-Fへ前倒ししPython 3.12を正式Supportする

- 文書ID: `adr_0015_phase_1f_lightning_and_python_312_support`
- 状態: `accepted`
- 作成日時: `2026-07-19 20:23:33 JST`
- 更新日時: `2026-07-19 20:23:33 JST`
- Snapshot: `20260719202333`
- Decision Owner: ユーザー
- 記録担当: 設計者役担当Task
- 正本言語: 日本語
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- Roadmap: [implementation_roadmap_20260719202333.md](../architecture/implementation_roadmap_20260719202333.md)
- supersedes: なし（ADR-0013を破棄せずPhase配置とPython Supportを具体化）

## Context

当初、Lightning AI Studio実装は後続のExternal Linux Phaseへ置いていた。一方、次の事情からPhase 1完了時点で一度公開する必要が生じた。

- ユーザーの生活上の期限
- Codex／GPT利用可能量と課金上の制約
- 各Phase完了時点でMacとLightningの両環境を比較検証したい
- 将来のModel／機材交換に備え、早期に第二Environmentを成立させたい

LightningのObserved EnvironmentはPython 3.12.11である。Current ProjectはSource Syntax上はPython 3.12で実行可能な見込みが高いが、Metadata、Lock、Static Tool、Setup／VerificationをPython 3.13専用へ固定している。

## Decision

1. Lightning AI Studio対応をPhase 6からPhase 1-Fへ前倒しする。
2. Phase 1の正式Support範囲をCPython 3.12／3.13へ広げる。
3. Local Mac PrimaryはCPython 3.13.14のままとする。
4. Lightningは既設CPython 3.12.11で開始し、期限のためだけに3.13へUpgradeしない。
5. `requires-python`、Lock、Ruff／Mypy基準をPython 3.12最小Supportへ整合させる。
6. Lightning CUDA Native RuntimeをPhase 1-Fの必須Gateとする。
7. Lightning CPU Profileも実装対象とするが、同一CUDA BuildでGPU未割当CPU実行が成立しない場合、期限と工数を再評価し、CPUを明示Known Limitationとして公開後Follow-upへ延期できる。
8. Phase 1-F完了後にMac／Lightningを含むUser Manual、Final Review、Backupを作り、その後に公開準備へ進む。

## Rationale

- Python 3.12はCurrent Sourceで使用するPEP 695 `type` statementの最小Versionであり、自然な下限である。
- `llama-cpp-python 0.3.34`は公式Package Metadata上Python 3.12をSupportする。
- uvもPython 3.12／3.13をTier 1 Supportする。
- Lightning既設Pythonを利用すれば、Python Upgrade自体を新しい変数にしない。
- 第二EnvironmentをPhase 1で成立させることで、Portable RuntimeというPhase名の実証力が上がる。

## Consequences

### Positive

- Mac MetalとLinux CUDAの交換性をPhase 1公開時点で示せる。
- 各後続Phaseを両環境で継続検証しやすくなる。
- Public Repositoryの再現性主張がMac単独より強くなる。
- Python 3.12利用者にも入口が広がる。

### Negative

- Current `uv.lock`の再生成と両Version Testが必要になる。
- Python 3.13専用Setup／VerificationをPlatform別に整理する必要がある。
- Container／CUDA Detection、CUDA Native Build、Model配置がPhase 1 Scopeへ追加される。
- Phase 1 User AcceptanceとBackupはPhase 1-F完了まで延期される。

## Publication Boundary

「公開URL」がGitHub Repository URLを意味する場合、Phase 1 CLI Runtimeの公開は可能である。

「Lightning上で操作できるLive Web URL」を意味する場合、Current Phase 1はCLIのみであるため、Web UI／API／Access Control／Port公開の追加要件が必要となる。両者を混同しない。

## Official References

- [uv Python support](https://docs.astral.sh/uv/reference/policies/python/)
- [uv Project Python configuration](https://docs.astral.sh/uv/concepts/projects/config/)
- [llama-cpp-python PyPI](https://pypi.org/project/llama-cpp-python/)

## Authorization Boundary

本ADRは設計DecisionをAcceptedとする。Source／Config／Lock／Setup変更、Lightning Package Install、Native Build、Model転送、GPU利用、Git／GitHub公開操作は、各担当への実装／外部操作許可後に行う。
