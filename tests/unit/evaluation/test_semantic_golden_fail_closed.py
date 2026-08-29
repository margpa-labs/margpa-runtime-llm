import json
from pathlib import Path
from typing import TypedDict, cast

import pytest

from margpa_runtime_llm.modules.evaluation.application.judge_output_decoder import (
    JudgeDecodeError,
    decode_judge_output,
)
from margpa_runtime_llm.modules.evaluation.application.judge_prompt_builder import (
    JudgePromptCriterion,
    build_judge_prompt,
)
from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import JudgeIndependenceClass


class _GoldenCase(TypedDict):
    case_id: str
    user_input: str
    candidate: str
    dialogue: list[str]
    evidence: list[str]
    criterion_id: str
    instruction: str


def test_four_manual_golden_cases_bind_context_and_reject_bare_accept() -> None:
    fixture_path = Path(__file__).parent / "fixtures/phase_6_semantic_golden_cases.json"
    cases = cast(list[_GoldenCase], json.loads(fixture_path.read_text(encoding="utf-8")))
    assert len(cases) == 4
    for item in cases:
        criterion_id = item["criterion_id"]
        prompt = build_judge_prompt(
            case=EvaluationCase(
                case_id=item["case_id"],
                input=item["user_input"],
                reference=None,
                criteria=(criterion_id,),
                language="en",
            ),
            candidate_answer=item["candidate"],
            rubric_id="phase_6_semantic_golden_v1",
            dialogue_context=tuple(item["dialogue"]),
            evidence_context=tuple(item["evidence"]),
            semantic_criteria=(
                JudgePromptCriterion(
                    criterion_id=criterion_id,
                    instruction=item["instruction"],
                    evaluation_method="classification_with_reference",
                    source_pointer=f"/golden/{item['case_id']}",
                ),
            ),
        )
        assert item["user_input"] in prompt
        assert item["candidate"] in prompt
        assert item["instruction"] in prompt
        for context in (*item["dialogue"], *item["evidence"]):
            assert context in prompt
        with pytest.raises(JudgeDecodeError, match="criterion_results"):
            decode_judge_output(
                raw_text='{"recommendation":"accept","confidence":0.95}',
                judge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
                token_usage=1,
                latency_ms=1,
                expected_criterion_ids=(criterion_id,),
            )
