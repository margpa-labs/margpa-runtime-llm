from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode


def test_default_mode_is_off() -> None:
    controller = JudgeModeController()
    snapshot = controller.mode_snapshot()
    assert snapshot.current_mode is EvaluationMode.OFF
    assert snapshot.revision == 1


def test_applying_a_new_mode_bumps_the_revision() -> None:
    controller = JudgeModeController()
    snapshot = controller.apply_mode(EvaluationMode.ENFORCE)
    assert snapshot.current_mode is EvaluationMode.ENFORCE
    assert snapshot.revision == 2


def test_reapplying_the_same_mode_does_not_bump_the_revision() -> None:
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    snapshot = controller.apply_mode(EvaluationMode.OBSERVE)
    assert snapshot.revision == 2
