from margpa_runtime_llm.modules.repair.application.repair_mode_controller import (
    RepairModeController,
)
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairMode


def test_default_mode_is_off() -> None:
    controller = RepairModeController()
    snapshot = controller.mode_snapshot()
    assert snapshot.current_mode is RepairMode.OFF
    assert snapshot.revision == 1


def test_applying_a_new_mode_bumps_the_revision() -> None:
    controller = RepairModeController()
    snapshot = controller.apply_mode(RepairMode.ENFORCE)
    assert snapshot.current_mode is RepairMode.ENFORCE
    assert snapshot.revision == 2


def test_reapplying_the_same_mode_does_not_bump_the_revision() -> None:
    controller = RepairModeController()
    controller.apply_mode(RepairMode.OBSERVE)
    snapshot = controller.apply_mode(RepairMode.OBSERVE)
    assert snapshot.revision == 2
