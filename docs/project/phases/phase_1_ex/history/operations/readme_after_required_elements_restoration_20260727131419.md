# MARGPA Runtime LLM

> Model-independent Runtime Governance research project by **Nazuna Research**

MARGPA Runtime LLMは、既存の言語モデルを交換可能な実行Componentとして扱い、その周囲にGovernance、評価、修復、証跡および実験のための共通基盤を構築する研究Projectです。

単一のChat UIや特定Modelの性能を完成目的とせず、異なるModel、Governance Definitionおよび周辺Componentを疎結合に接続し、構成差と介入結果を比較・検証できるRuntime Kernelを目指しています。

> **現在地：Phase 1-ex / 最終予定 Phase 10**
>
> Phase 1は完了・Accepted済みです。現在位置、実装済み範囲、未実装範囲および将来構想は、[Roadmap](docs/public/roadmap_ja.md)を正本としてご確認ください。

## 最初にRoadmapをご覧ください

現在の画面や機能はProject全体の初期段階です。本Projectが最終的に何を統治・比較・検証しようとしているか、また各能力をどの順序で成立させるかは、Roadmapにまとめています。

**[MARGPA Runtime LLM Roadmap](docs/public/roadmap_ja.md)**

## Projectの特徴

- 特定のModelやGovernance DefinitionをCoreへHardcodeしない。
- Model、Governance、評価、修復、証跡およびInterfaceの責務を分離する。
- 存在、評価、Authority、Approval、ExecutionおよびResponsibilityを混同しない。
- 同じ条件で構成差、介入結果、CostおよびFailureを比較できる研究基盤を目指す。

## Project文書

- [概要](docs/public/overview_ja.md)
- [コンセプト](docs/public/concept_ja.md)
- [Roadmap](docs/public/roadmap_ja.md)
- [要件定義書](docs/project/current/requirements/requirements_specification_ja.md)
- [全体設計書](docs/project/current/architecture/system_architecture_ja.md)
- [技術選定書](docs/project/current/architecture/technology_selection_ja.md)
- [基本設計書](docs/project/current/architecture/basic_design_ja.md)
- [Runtime Governance仕様書](docs/project/current/governance/runtime_governance_specification_ja.md)

## 現在の画面

現時点の画面例です。画面はProject全体の完成像を示すものではありません。

![MARGPA Runtime LLM demo 1](assets/images/margpa-runtime-llm_demo_image_1.png)

![MARGPA Runtime LLM demo 2](assets/images/margpa-runtime-llm_demo_image_2.png)

![MARGPA Runtime LLM demo 3](assets/images/margpa-runtime-llm_demo_image_3.png)

![MARGPA Runtime LLM demo 4](assets/images/margpa-runtime-llm_demo_image_4.png)

![MARGPA Runtime LLM demo 5](assets/images/margpa-runtime-llm_demo_image_5.png)

![MARGPA Runtime LLM demo 6](assets/images/margpa-runtime-llm_demo_image_6.png)

## Research Preview

本Repositoryは研究・評価段階のPreviewであり、現時点ではOpen Sourceではありません。Model Weightは同梱しておらず、第三者のModel、Software、DefinitionおよびServiceには、それぞれ独立した利用条件が適用されます。

利用可能な範囲、禁止事項、第三者Artifactの取扱いおよび免責事項は、次の文書を正本とします。

- [LICENSE](LICENSE)
- [TERMS_OF_USE.md](TERMS_OF_USE.md)
- [NOTICE.md](NOTICE.md)
- [CITATION.cff](CITATION.cff)

## 重要な留意事項

- 本Projectは研究・検証中のPrototypeです。
- LLMの出力には、誤り、欠落、不適切な内容および予期しない挙動が含まれる可能性があります。
- 動作、互換性、正確性、安全性、完全性、可用性および特定目的への適合性を含め、一切の保証を行いません。
- 各文書は修正する必要性があるため、都度内容が変更される可能性があります。
- 実装状態と計画はRoadmap、利用条件と免責の詳細はLICENSE、TERMS_OF_USEおよびNOTICEを優先してください。

## English Abstract

MARGPA Runtime LLM is a model-independent research project for treating governance definitions, language models, evaluation, repair, evidence, and related runtime components as separable and testable parts of a common governance execution and experimentation kernel. The current implementation is an early foundation rather than the final project scope. See the [Roadmap](docs/public/roadmap_ja.md) for the authoritative implementation status and planned progression.
