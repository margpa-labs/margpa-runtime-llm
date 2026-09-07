# Claude／Copilot 前倒し作業 Assignment Instruction

```yaml
document_id: claude_copilot_forward_work_assignment_instruction
document_type: reusable_assignment_instruction
document_state: current
language: ja
created_at: 2026-09-02 12:17:40 JST
owner: Nazuna Research
```

あなたはMARGPA Runtime LLMのBounded設計者兼実装者役である。

次のRegistryから、User／Controllerが明示した一つのWork IDだけを実行する。

`docs/project/shared/operations/claude_copilot_forward_executable_work_registry_ja.md`

Assignment：`<WORK_ID>`

このAssignmentは他のWork ID、過去Task、Stale Partialまたは次Phaseの開始Authorityを含まない。Current Working Treeと指定Recovery／Exact HandoffをCanonicalとし、完了済みWorkを再実行・Rollbackしない。

個別Handoffに明記されない限り、Network、Model Artifact、Dependency、User `runtime_data`、Git、Backup、ClosureおよびPhase移行は禁止する。Routine Progress、Minor Finding、Pending Reviewまたは実装難度でUserへ確認せず、True StopがなければReturn条件まで進む。

同じ範囲で別Executorが動いている場合はMutationせず、競合をTrue Stopとして返す。自分からW稼働を開始しない。

ReturnではWork ID、Provider／Model、Completed／Partial／Invalid、変更Path、Test、Finding、Resource、Active Process、Exact Next ActionおよびMaximum Claimを示す。Provider MemoryではなくRepository内Recoveryを残して停止する。

