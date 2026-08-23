"""RuntimeEvent Envelope (Architecture 9.1).

component_role and point_id are plain, extensible strings, never a closed
Enum (matching the existing governance_definitions Point ID convention):
new components/points must not require a Core code change to be named.
"""

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

SafePayloadValue = str | int | float | bool
POINT_ID_PATTERN = r"^[a-z][a-z0-9_.]*$"


class RuntimeEvent(ImmutableContract):
    event_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    conversation_id: str | None = None
    turn_id: str | None = None
    generation_attempt_id: str | None = None
    evaluation_run_id: str | None = None
    repair_attempt_id: str | None = None
    component_role: str = Field(min_length=1, pattern=POINT_ID_PATTERN)
    point_id: str = Field(min_length=1, pattern=POINT_ID_PATTERN)
    state: str = Field(min_length=1)
    timestamp: str = Field(min_length=1)
    safe_payload: dict[str, SafePayloadValue] = Field(default_factory=dict)
    config_ref: str | None = None
    artifact_ref: str | None = None
    definition_ref: str | None = None
