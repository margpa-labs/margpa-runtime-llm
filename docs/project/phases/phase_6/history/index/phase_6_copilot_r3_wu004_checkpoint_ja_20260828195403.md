# Phase 6 Copilot R3 WU-004 Checkpoint

```yaml
document_type: phase_work_unit_checkpoint
document_state: append_only
provider: GitHub Copilot app
package: P6-RR-R3
work_unit: R3-WU-004
status: COMPLETE
```

Budget選択外は`budget_exhausted`、Built-inの非対応Mappingは`unsupported_mapping`、Provider `none`/`unavailable`/`failed`は別Reasonに正規化した。新規RegressionはProvider Failureが`malformed_result`へ誤分類されないことを固定する。
