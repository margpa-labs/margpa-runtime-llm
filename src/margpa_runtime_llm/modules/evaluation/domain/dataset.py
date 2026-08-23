"""EvaluationDataset/EvaluationCase (Architecture 6.1)."""

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

SHA512_PATTERN = r"^[0-9a-f]{128}$"


class EvaluationDataset(ImmutableContract):
    dataset_id: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    digest_sha512: str = Field(pattern=SHA512_PATTERN)
    source_class: str = Field(min_length=1)


class EvaluationCase(ImmutableContract):
    case_id: str = Field(min_length=1)
    input: str = Field(min_length=1)
    reference: str | None = None
    criteria: tuple[str, ...] = Field(min_length=1)
    language: str = Field(min_length=1)
    tags: tuple[str, ...] = ()
