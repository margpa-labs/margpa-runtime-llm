from margpa_runtime_llm.modules.runtime_observability.application.recording_mode_controller import (
    RecordingModeController,
)
from margpa_runtime_llm.modules.runtime_observability.domain.recording import RecordingMode


def test_default_mode_is_off() -> None:
    controller = RecordingModeController()
    snapshot = controller.mode_snapshot()
    assert snapshot.current_mode is RecordingMode.OFF
    assert snapshot.revision == 1


def test_applying_a_new_mode_bumps_the_revision() -> None:
    controller = RecordingModeController()
    snapshot = controller.apply_mode(RecordingMode.FULL)
    assert snapshot.current_mode is RecordingMode.FULL
    assert snapshot.revision == 2


def test_reapplying_the_same_mode_does_not_bump_the_revision() -> None:
    controller = RecordingModeController()
    controller.apply_mode(RecordingMode.METADATA)
    snapshot = controller.apply_mode(RecordingMode.METADATA)
    assert snapshot.revision == 2
