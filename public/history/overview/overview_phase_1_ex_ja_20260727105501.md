# MARGPA Runtime LLM 概要

```yaml
document_id: public_overview
status: current
language: ja
created_at: 2026-07-27 10:49:00 JST
updated_at: 2026-07-27 10:49:00 JST
owner: Nazuna Research
active_phase: phase_1_ex
```

MARGPA Runtime LLMは、Hugging Face由来の事前学習済みオープンモデルを利用し、モデルの外側から推論、文脈、監査、評価、修復および実行状態を統治する、モデル非依存のRuntime Governance型AI研究基盤である。

目的は、特定のモデルやUIへ密結合したChat Applicationを作ることではない。Model、Backend、Configuration、Governance Definition、Guardrail、Judge、Repair、RAG、Agent、Storage、UIおよびDeploymentを分離し、個別に交換・無効化・比較できる構造を作る。将来、現在の軽量モデルを高性能モデルへ交換しても、Application CoreとGovernance Coreを維持したまま継続できることを重視する。

Phase 1では、Apple M2 Pro／16GB上のQwen3-4B GGUFと`llama.cpp`系Backendを用い、CLI、Streaming、生成停止、複数Turnの一時会話、言語切替、Thinking制御、要約モードおよび最小Web UIを成立させた。Lightning AI StudioのLinux x86_64 Pure CPU環境でも、環境再構築、Test、Model生成、外部BrowserからのBasic Previewを確認した。

現在はPhase 1-exで、長期研究・Task間継承・公開に耐えるDocs、Lossless History、役割権限、利用条件、Public Demo境界、簡易Documentation RAGおよびGit運用を整備している。Phase 1-exは進行中であり、匿名Public Demo、GitHub公開、Mac限定簡易RAGおよびTraffic-aware Wake-upはまだ成立済みではない。

本Projectの全体像と将来計画は、[Roadmap](roadmap_ja.md)を参照してほしい。現在のUIはRootの`assets/images/`にあるDemo画像で確認できる。

本Projectは研究Previewであり、動作、互換性、正確性、安全性、可用性および特定目的への適合性を保証しない。Repositoryの利用条件はRootの`LICENSE`と`TERMS_OF_USE.md`を正本とする。
