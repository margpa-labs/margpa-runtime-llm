# ADR-0016 Canonical ModelとDeployment Artifactの分離

- 文書ID: `adr_0016_canonical_model_and_deployment_artifact_separation`
- 状態: `accepted`
- 作成日時: `2026-07-20 23:10:36 JST`
- 更新日時: `2026-07-20 23:10:36 JST`
- Snapshot: `20260720231036`
- Decision Owner: ユーザー
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: なし

## 1. Context

Guard ModelとJudge Modelについて、現在保有する第三者GGUF量子化Artifactを継続するか、将来を考慮してUpstream開発元の通常Weightへ切り替えるかを再評価した。

対象：

```text
Guard Local Artifact:
  DevQuasar/Qwen.Qwen3Guard-Gen-0.6B-GGUF
  Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf

Judge Local Artifact:
  bartowski/Selene-1-Mini-Llama-3.1-8B-GGUF
  Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf
```

## 2. Decision

Modelの出自正本と、特定環境で実際にLoadするArtifactを分離する。

```text
Canonical Model Source
  ↓ conversion／quantization relation
Deployment Artifact
  ↓ backend binding
Runtime Model Instance
```

採用関係：

| Role | Canonical Model Source | Local Deployment Artifact | Future Cloud Artifact |
|---|---|---|---|
| Guard | `Qwen/Qwen3Guard-Gen-0.6B` | DevQuasar GGUF `Q8_0` | Qwen公式Safetensors等 |
| Judge | `AtlaAI/Selene-1-Mini-Llama-3.1-8B` | bartowski GGUF `Q5_K_M` | AtlaAI公式Safetensors等 |

現在のGGUFを削除・置換せず、Mac／llama.cpp用Artifactとして維持する。公式通常Weightは実装上必要になるまでDownloadしない。

## 3. Rationale

- 公式通常WeightはModelの出自、Tokenizer、Config、Prompt形式、Revisionの正本として扱いやすい
- GGUFはMac／llama.cppでMemory効率と導入容易性に優れる
- M2 Pro／16GBでSelene BF16 Weightを常用するのは現実的でない
- 量子化Artifactを使用しても、Upstream、Revision、Conversion、Hashを明示すればProvenanceを保持できる
- Local／Cloudを同一Formatへ固定する必要はなく、Model Port／Backend Adapterで分離できる
- Formatの優劣ではなく、Canonical IdentityとDeployment適性を別々に管理する方が疎結合である

## 4. Guard固有判断

`Qwen/Qwen3Guard-Gen-0.6B`をCanonical Sourceとする。現在のDevQuasar Q8_0は約805MBのLocal Artifactとして継続する。

将来、生成後判定だけでなくToken単位のStreaming監視を本格化する場合は、`Qwen3Guard-Stream`系列も別Capabilityとして再評価する。`Gen`と`Stream`を同一Modelとして扱わない。

## 5. Judge固有判断

`AtlaAI/Selene-1-Mini-Llama-3.1-8B`をCanonical Sourceとする。現在のbartowski Q5_K_Mは約5.73GBのOn-Demand Local Artifactとして継続する。

Selene Miniは公式説明上、主に英語を対象とし、日本語は明示対応言語に含まれない。このため次を必須とする。

- 日本語Judge性能を未保証とする
- 日本語Evaluation Setで独立検証する
- 唯一のJudgeまたは最終権限として固定しない
- Rule Based評価、User評価、他Judge候補と比較できるようにする
- 日本語性能が不足する場合はQwen系等の別Judgeへ交換可能にする

## 6. Registry Consequence

Model Registryは最低限次を別Fieldとして持つ。

- Canonical Provider／Repository／Revision
- Canonical Config／Tokenizer／License
- Artifact Distributor／Repository／Revision
- Artifact File／Format／Quantization／Size／Hash
- Conversion Tool／Version／Parameters／Dataset情報（取得可能な場合）
- Backend／Backend Version
- Prompt／Chat Template／Parser
- Local／Cloud Deployment Profile
- Verification State／Evaluation Result

## 7. Alternatives Rejected

### 公式通常Weightだけへ即時統一

現在のMac、llama.cpp、Memory制約、Phase優先順位に合わないため不採用。

### GGUFだけをModelの正本にする

Upstreamとの関係、Cloud Backend、Tokenizer／ConfigのCanonical情報が弱くなるため不採用。

### 公式WeightとGGUFを今すぐ両方Download

現在の実装に不要でStorageと管理対象だけを増やすため不採用。

## 8. Sources

- Qwen Guard Canonical: `https://huggingface.co/Qwen/Qwen3Guard-Gen-0.6B`
- Qwen Guard Local GGUF: `https://huggingface.co/DevQuasar/Qwen.Qwen3Guard-Gen-0.6B-GGUF`
- Selene Canonical: `https://huggingface.co/AtlaAI/Selene-1-Mini-Llama-3.1-8B`
- Selene Local GGUF: `https://huggingface.co/bartowski/Selene-1-Mini-Llama-3.1-8B-GGUF`
- AtlaAI GGUF Reference: `https://huggingface.co/AtlaAI/Selene-1-Mini-Llama-3.1-8B-Q8_0-GGUF`

## 9. Authorization Boundary

本DecisionはModel Metadataと将来Backend方針を確定する。Model Download、現行GGUF削除、Model配置変更、Dependency追加、Adapter実装、Cloud Deploymentを許可しない。

