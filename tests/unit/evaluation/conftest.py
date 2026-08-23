from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode, EvaluatorClass
from margpa_runtime_llm.modules.evaluation.domain.run import (
    EvaluationBudget,
    EvaluationRun,
    EvaluatorBinding,
)

SHA512_FILLER = "f" * 128


def make_case(*, case_id: str = "case-1") -> EvaluationCase:
    return EvaluationCase(
        case_id=case_id,
        input="What is the capital of France?",
        reference="Paris",
        criteria=("exact_reference_match",),
        language="en",
    )


def make_run(*, mode: EvaluationMode, run_id: str = "run-1") -> EvaluationRun:
    return EvaluationRun(
        run_id=run_id,
        request_id="req-1",
        dataset_id="dataset-1",
        case_id="case-1",
        criteria=("exact_reference_match",),
        evaluator_binding=EvaluatorBinding(
            evaluator_id="exact_reference_match_v1",
            evaluator_class=EvaluatorClass.DETERMINISTIC,
        ),
        mode=mode,
        config_digest=SHA512_FILLER,
        budget=EvaluationBudget(max_calls=1, max_tokens=1000, max_wall_time_ms=5000),
    )
