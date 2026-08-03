# NOTICE

## 日本語

### Project

```text
名称          : MARGPA Runtime LLM
公開・研究名義: Nazuna Research
Repository    : margpa-labs/margpa-runtime-llm
状態          : Research Preview
```

Copyright © 2026 Nazuna Research. All rights reserved.

本Repositoryの独自成果物にはRootの`LICENSE`と`TERMS_OF_USE.md`が適用される。現段階ではOpen Sourceではない。

### Model

Model Weightは本Repositoryへ含めない。

Current Main Model候補：

```text
Upstream／Repository : Qwen/Qwen3-4B
Distribution         : Qwen/Qwen3-4B-GGUF
Local Artifact       : Qwen3-4B-Q4_K_M.gguf
```

Model名の記載は、各権利者による本Projectへの承認、提携または保証を意味しない。Modelの取得・利用には、配布元のModel Card、Licenseおよび利用条件が独立して適用される。

Guard候補のQwen3Guard-Gen-0.6B、Judge候補のAtlaAI/Selene-1-Mini-Llama-3.1-8Bも現時点では本Runtimeへ統合しておらず、WeightをRepositoryへ含めない。

### 第三者Software

本ProjectはPython Packageその他の第三者Softwareへ依存する。Versionは`pyproject.toml`と`uv.lock`を参照する。各Componentの著作権とLicenseは各権利者に帰属し、RootのResearch Preview Licenseで上書きしない。

### ARGD／DAGD

Runtime Governanceの参照元であるARGD v0.3.1／DAGD v0.4.4は、License `CC-BY-SA-4.0`として原Definitionに記録されている。

公開Repositoryへ原Definitionを含める場合は、CC-BY-SA-4.0のAttribution、ShareAlikeその他の条件を満たす必要がある。現時点の本Repositoryには原Definition JSONを含めていない。Documentation上の名称・構造説明は、将来の実装・統合方針を示すものである。

原Definitionを将来含める場合のAuthor表記と公開名義の整合は、配布前のAttribution Reviewで確定する。Projectの公開名義は`Nazuna Research`である。

### EASA／DLAGSA／OCILNS

EASA、DLAGSAおよびOCILNSはNazuna Researchの独立R&D構想である。現時点で公開しているのは名称、研究領域、概要およびMARGPA Runtime LLMとの将来接続方向であり、詳細Algorithm、内部Protocolまたは改竄耐性方式を公開したことを意味しない。

### 無保証

本Project、Documentation、Code、Configuration、Hosted Demo、Model連携およびOutputについて、動作、互換性、正確性、安全性、完全性、可用性または特定目的への適合性を一切保証しない。

## English

### Project

```text
Name             : MARGPA Runtime LLM
Public identity  : Nazuna Research
Repository       : margpa-labs/margpa-runtime-llm
Status           : Research Preview
```

Copyright © 2026 Nazuna Research. All rights reserved.

The original repository materials are governed by the root `LICENSE` and
`TERMS_OF_USE.md`. This project is not open source at this stage.

### Models

Model weights are not included in this repository. References to Qwen,
Qwen3Guard, Selene, AtlaAI, or other third-party names do not imply endorsement,
partnership, or warranty. Each model is governed by its own model card, license,
and terms.

### Third-Party Software

This project depends on third-party software. Versions are recorded in
`pyproject.toml` and `uv.lock`. Copyright and license terms for those components
remain with their respective rights holders and are not replaced by the MARGPA
Research Preview License.

### ARGD and DAGD

The referenced original definitions ARGD v0.3.1 and DAGD v0.4.4 identify
`CC-BY-SA-4.0` as their license. If the original definition files are included
in a future public distribution, the applicable attribution, ShareAlike, and
other license requirements must be satisfied. The original JSON definition
file is not included in the current repository.

The author attribution and its consistency with the public project identity
must be resolved by an attribution review before such a distribution. The
public identity of this project is `Nazuna Research`.

### EASA, DLAGSA, and OCILNS

EASA, DLAGSA, and OCILNS are independent R&D concepts of Nazuna Research. The
current public materials disclose their names, research areas, short
descriptions, and future integration direction only. They do not disclose
their core algorithms, internal protocols, or tamper-resistance mechanisms.

### No Warranty

The project, documentation, code, configuration, hosted demonstrations, model
integrations, and outputs are provided without warranties of operation,
compatibility, accuracy, safety, completeness, availability, or fitness for a
particular purpose.
