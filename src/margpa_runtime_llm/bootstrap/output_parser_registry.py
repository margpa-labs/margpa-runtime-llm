"""Build an output parser from a model-declared protocol definition."""

from margpa_runtime_llm.adapters.output_protocols.plain_text import PlainTextOutputParser
from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import (
    TaggedThinkingOutputParser,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.inference.domain.model_definition import (
    ThinkingOutputProtocolDefinition,
)
from margpa_runtime_llm.modules.presentation.ports.thinking_output_parser import (
    ThinkingOutputParser,
)


def build_output_parser(
    definition: ThinkingOutputProtocolDefinition,
) -> ThinkingOutputParser:
    if definition.parser_key == "plain_text_v1":
        return PlainTextOutputParser()
    if definition.parser_key == "tagged_thinking_v1":
        if definition.opening_delimiter is None or definition.closing_delimiter is None:
            raise InferenceError(
                code=InferenceErrorCode.INVALID_MODEL_DEFINITION,
                safe_message="The tagged thinking output protocol is incomplete.",
            )
        return TaggedThinkingOutputParser(
            opening_delimiter=definition.opening_delimiter,
            closing_delimiter=definition.closing_delimiter,
        )
    raise InferenceError(
        code=InferenceErrorCode.INVALID_MODEL_DEFINITION,
        safe_message="The model output parser is not registered.",
        details={"parser_key": definition.parser_key},
    )
