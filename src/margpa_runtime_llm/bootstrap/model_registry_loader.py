"""Load and validate a single TOML model registry definition."""

from __future__ import annotations

import hashlib
import tomllib
from pathlib import Path

from pydantic import ValidationError

from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition


def load_model_definition(path: Path) -> ModelDefinition:
    """Return a validated definition with its source-file SHA-512 attached."""

    try:
        raw_definition = path.read_bytes()
        data = tomllib.loads(raw_definition.decode("utf-8"))
        data["definition_file_sha512"] = hashlib.sha512(raw_definition).hexdigest()
        return ModelDefinition.model_validate(data)
    except FileNotFoundError as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_MODEL_DEFINITION,
            safe_message="The model registry definition was not found.",
            details={"exception_type": type(exc).__name__},
        ) from exc
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValidationError) as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_MODEL_DEFINITION,
            safe_message="The model registry definition is invalid.",
            details={"exception_type": type(exc).__name__},
        ) from exc
