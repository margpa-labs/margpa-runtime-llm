"""Production llama.cpp Model Port adapter."""

from __future__ import annotations

import gc
import hashlib
import importlib.metadata
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

from llama_cpp import Llama, llama_cpp

from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationRequest,
    GenerationResult,
    GenerationStream,
    GenerationTiming,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    GpuOffloadEvidence,
    ModelCapabilities,
    ModelDigest,
    ModelLoadConfig,
    ModelRuntimeInfo,
)
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
from margpa_runtime_llm.modules.inference.domain.capabilities import (
    MODEL_REQUIRED_CAPABILITIES,
    CapabilityFeature,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.inference.domain.lifecycle import ModelLifecycleState
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition

from .chat_template import LlamaCppChatTemplate
from .error_mapping import map_finish_reason, parse_token_usage, raise_mapped_backend_error
from .repetition import PathologicalRepetitionDetector, detect_pathological_repetition
from .runtime_detection import (
    detect_llama_cpp_build_variant,
    detect_llama_cpp_device,
    observe_nvidia_process_gpu_memory,
)
from .stream import LlamaCppGenerationStream


class LlamaCppModelAdapter:
    """Own exactly one loaded llama.cpp model and one active generation."""

    def __init__(self, *, model_root: Path) -> None:
        self._model_root = model_root.expanduser().resolve()
        self._state = ModelLifecycleState.UNLOADED
        self._state_lock = threading.RLock()
        self._generation_lock = threading.Lock()
        self._model: Llama | None = None
        self._definition: ModelDefinition | None = None
        self._load_config: ModelLoadConfig | None = None
        self._runtime_info: ModelRuntimeInfo | None = None
        self._chat_template: LlamaCppChatTemplate | None = None

    @property
    def state(self) -> ModelLifecycleState:
        with self._state_lock:
            return self._state

    @property
    def runtime_info(self) -> ModelRuntimeInfo | None:
        with self._state_lock:
            return self._runtime_info

    def load(
        self,
        definition: ModelDefinition,
        config: ModelLoadConfig,
    ) -> ModelRuntimeInfo:
        with self._state_lock:
            if self._runtime_info is not None:
                if self._runtime_info.model_key == definition.model_key:
                    return self._runtime_info
                raise InferenceError(
                    code=InferenceErrorCode.MODEL_ALREADY_LOADED,
                    safe_message="A different model is already loaded.",
                    model_key=definition.model_key,
                )
            if self._state is not ModelLifecycleState.UNLOADED:
                raise InferenceError(
                    code=InferenceErrorCode.MODEL_LOAD_FAILED,
                    safe_message="The model port is not ready to load a model.",
                    model_key=definition.model_key,
                )
            self._state = ModelLifecycleState.LOADING

        model: Llama | None = None
        try:
            self._validate_definition(definition, config)
            artifact_path, artifact_digest = self._verify_artifact(definition)
            model = Llama(
                model_path=str(artifact_path),
                n_gpu_layers=config.gpu_layers,
                n_ctx=config.context_size,
                n_batch=config.batch_size,
                n_ubatch=config.micro_batch_size,
                n_threads=config.threads,
                n_threads_batch=config.threads_batch,
                use_mmap=config.use_mmap,
                use_mlock=config.use_mlock,
                verbose=config.verbose_backend,
            )
            chat_template = LlamaCppChatTemplate(model)
            runtime_info = self._build_runtime_info(
                definition,
                config,
                model,
                chat_template,
                artifact_digest,
            )
            with self._state_lock:
                self._model = model
                self._definition = definition
                self._load_config = config
                self._chat_template = chat_template
                self._runtime_info = runtime_info
                self._state = ModelLifecycleState.LOADED
            return runtime_info
        except InferenceError:
            if model is not None:
                model.close()
            with self._state_lock:
                self._state = ModelLifecycleState.FAILED
            raise
        except (KeyboardInterrupt, SystemExit):
            if model is not None:
                try:
                    model.close()
                except Exception:
                    pass
            with self._state_lock:
                self._state = ModelLifecycleState.FAILED
            raise
        except Exception as exc:
            if model is not None:
                model.close()
            with self._state_lock:
                self._state = ModelLifecycleState.FAILED
            raise_mapped_backend_error("load", exc, model_key=definition.model_key)

    def unload(self) -> None:
        with self._state_lock:
            if self._state is ModelLifecycleState.UNLOADED:
                return
            if self._state is ModelLifecycleState.GENERATING:
                raise InferenceError(
                    code=InferenceErrorCode.MODEL_BUSY,
                    safe_message="The model cannot be unloaded while generation is active.",
                    retryable=True,
                    model_key=self._definition.model_key if self._definition is not None else None,
                )
            self._state = ModelLifecycleState.UNLOADING
            model = self._model
        try:
            if model is not None:
                model.close()
            gc.collect()
            with self._state_lock:
                self._model = None
                self._definition = None
                self._load_config = None
                self._chat_template = None
                self._runtime_info = None
                self._state = ModelLifecycleState.UNLOADED
        except (KeyboardInterrupt, SystemExit):
            with self._state_lock:
                self._state = ModelLifecycleState.FAILED
            raise
        except Exception as exc:
            with self._state_lock:
                self._state = ModelLifecycleState.FAILED
            raise_mapped_backend_error("unload", exc)

    def capabilities(self) -> ModelCapabilities:
        runtime_info = self.runtime_info
        if runtime_info is None:
            raise InferenceError(
                code=InferenceErrorCode.MODEL_NOT_LOADED,
                safe_message="The model is not loaded.",
            )
        return runtime_info.effective_capabilities

    def generate(
        self,
        request: GenerationRequest,
        *,
        cancellation: CancellationToken | None = None,
    ) -> GenerationResult:
        model, chat_template, runtime_info = self._begin_generation(request)
        started = time.perf_counter()
        try:
            self._validate_context(request, chat_template, runtime_info)
            raw_response = chat_template.create_chat_completion(
                request.messages,
                request.parameters,
                stream=False,
                cancellation=cancellation,
            )
            response = cast(dict[str, Any], raw_response)
            choices = response.get("choices")
            if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
                raise InferenceError(
                    code=InferenceErrorCode.BACKEND_PROTOCOL_ERROR,
                    safe_message="The model backend returned an invalid completion.",
                    request_id=request.request_id,
                    model_key=request.model_key,
                )
            choice = choices[0]
            message = choice.get("message")
            content = message.get("content", "") if isinstance(message, dict) else ""
            if not isinstance(content, str):
                raise InferenceError(
                    code=InferenceErrorCode.BACKEND_PROTOCOL_ERROR,
                    safe_message="The model backend returned non-text content.",
                    request_id=request.request_id,
                    model_key=request.model_key,
                )
            if detect_pathological_repetition(content):
                self._mark_generation_unavailable()
                raise InferenceError(
                    code=InferenceErrorCode.GENERATION_FAILED,
                    safe_message=(
                        "The model produced an unstable repetitive response and was stopped safely."
                    ),
                    retryable=True,
                    request_id=request.request_id,
                    model_key=request.model_key,
                    details={"reason": "pathological_repetition_detected"},
                )
            finish_reason, backend_finish_reason = map_finish_reason(choice.get("finish_reason"))
            if cancellation is not None and cancellation.is_cancelled():
                # P6-CODEX-019: a Main-priority preemption stops the token
                # loop via `stopping_criteria`, which llama.cpp itself
                # reports as an ordinary "stop" — only the caller-held
                # Cancellation Token can distinguish "stopped because the
                # caller wants to actually stop" from a genuine content
                # stop. Never conflated with a real completed answer.
                finish_reason = FinishReason.CANCELLED
            usage = parse_token_usage(response)
            total_seconds = time.perf_counter() - started
            tokens_per_second = (
                usage.completion_tokens / total_seconds
                if usage is not None and total_seconds > 0
                else None
            )
            return GenerationResult(
                request_id=request.request_id,
                model_key=request.model_key,
                content=content,
                finish_reason=finish_reason,
                backend_finish_reason=backend_finish_reason,
                usage=usage,
                timing=GenerationTiming(
                    first_content_latency_seconds=None,
                    total_generation_seconds=total_seconds,
                    tokens_per_second=tokens_per_second,
                ),
                runtime_info=runtime_info.reference(),
                warnings=runtime_info.warnings,
            )
        except InferenceError:
            raise
        except Exception as exc:
            raise_mapped_backend_error(
                "generation",
                exc,
                request_id=request.request_id,
                model_key=request.model_key,
            )
        finally:
            del model
            self._end_generation()

    def stream(self, request: GenerationRequest) -> GenerationStream:
        _, chat_template, runtime_info = self._begin_generation(request)
        try:
            prompt_tokens = self._validate_context(request, chat_template, runtime_info)
            raw_stream = chat_template.create_chat_completion(
                request.messages,
                request.parameters,
                stream=True,
            )
            native_stream = cast(Iterator[dict[str, Any]], raw_stream)
            return LlamaCppGenerationStream(
                generation_id=str(uuid4()),
                request_id=request.request_id,
                model_key=request.model_key,
                native_stream=native_stream,
                on_terminal=self._end_generation,
                fallback_prompt_tokens=prompt_tokens,
                completion_text_token_counter=chat_template.count_text_tokens,
                repetition_detector=PathologicalRepetitionDetector(),
                on_pathological_output=self._mark_generation_unavailable,
            )
        except InferenceError:
            self._end_generation()
            raise
        except (KeyboardInterrupt, SystemExit):
            self._end_generation()
            raise
        except Exception as exc:
            self._end_generation()
            raise_mapped_backend_error(
                "stream",
                exc,
                request_id=request.request_id,
                model_key=request.model_key,
            )

    def count_text_tokens(self, text: str) -> int:
        with self._state_lock:
            if not self._generation_lock.acquire(blocking=False):
                raise InferenceError(
                    code=InferenceErrorCode.MODEL_BUSY,
                    safe_message="The model is already processing another request.",
                    retryable=True,
                )
            try:
                if self._state is not ModelLifecycleState.LOADED or self._chat_template is None:
                    raise InferenceError(
                        code=InferenceErrorCode.MODEL_NOT_LOADED,
                        safe_message="The model is not loaded.",
                    )
                return self._chat_template.count_text_tokens(text)
            finally:
                self._generation_lock.release()

    def count_chat_prompt_tokens(
        self,
        messages: tuple[ChatMessage, ...],
        thinking_mode: ThinkingMode,
    ) -> int:
        with self._state_lock:
            if not self._generation_lock.acquire(blocking=False):
                raise InferenceError(
                    code=InferenceErrorCode.MODEL_BUSY,
                    safe_message="The model is already processing another request.",
                    retryable=True,
                )
            try:
                if self._state is not ModelLifecycleState.LOADED or self._chat_template is None:
                    raise InferenceError(
                        code=InferenceErrorCode.MODEL_NOT_LOADED,
                        safe_message="The model is not loaded.",
                    )
                return self._chat_template.format_prompt(messages, thinking_mode).token_count
            finally:
                self._generation_lock.release()

    def __enter__(self) -> LlamaCppModelAdapter:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.unload()

    def _begin_generation(
        self,
        request: GenerationRequest,
    ) -> tuple[Llama, LlamaCppChatTemplate, ModelRuntimeInfo]:
        with self._state_lock:
            if self._state is ModelLifecycleState.GENERATING or not self._generation_lock.acquire(
                blocking=False
            ):
                raise InferenceError(
                    code=InferenceErrorCode.MODEL_BUSY,
                    safe_message="The model is already processing another request.",
                    retryable=True,
                    request_id=request.request_id,
                    model_key=request.model_key,
                )
            if (
                self._state is not ModelLifecycleState.LOADED
                or self._model is None
                or self._chat_template is None
                or self._runtime_info is None
            ):
                self._generation_lock.release()
                raise InferenceError(
                    code=InferenceErrorCode.MODEL_NOT_LOADED,
                    safe_message="The model is not loaded.",
                    request_id=request.request_id,
                    model_key=request.model_key,
                )
            if self._runtime_info.model_key != request.model_key:
                self._generation_lock.release()
                raise InferenceError(
                    code=InferenceErrorCode.INVALID_REQUEST,
                    safe_message="The requested model does not match the loaded model.",
                    request_id=request.request_id,
                    model_key=request.model_key,
                )
            self._state = ModelLifecycleState.GENERATING
            return self._model, self._chat_template, self._runtime_info

    def _end_generation(self) -> None:
        with self._state_lock:
            if self._state is ModelLifecycleState.GENERATING:
                self._state = ModelLifecycleState.LOADED
            if self._generation_lock.locked():
                self._generation_lock.release()

    def _mark_generation_unavailable(self) -> None:
        """Trip a process-local circuit breaker for an unstable Model load.

        A detected pathological loop is not treated as a clean completion and
        the same load instance is not allowed to serve another request. A
        controlled unload/switch may still recover or roll back normally.
        """

        with self._state_lock:
            if self._state is ModelLifecycleState.GENERATING:
                self._state = ModelLifecycleState.FAILED

    @staticmethod
    def _validate_context(
        request: GenerationRequest,
        chat_template: LlamaCppChatTemplate,
        runtime_info: ModelRuntimeInfo,
    ) -> int:
        """Fail-closed context check; returns the formatted prompt's token count
        so callers needing it (e.g. streaming's usage fallback) avoid a second
        tokenization pass."""

        prompt = chat_template.format_prompt(request.messages, request.parameters.thinking_mode)
        required_tokens = prompt.token_count + request.parameters.max_new_tokens
        available_tokens = runtime_info.loaded_context_size
        if required_tokens > available_tokens:
            raise InferenceError(
                code=InferenceErrorCode.CONTEXT_LIMIT_EXCEEDED,
                safe_message="The formatted prompt and requested output exceed the loaded context.",
                request_id=request.request_id,
                model_key=request.model_key,
                details={
                    "prompt_tokens": prompt.token_count,
                    "max_new_tokens": request.parameters.max_new_tokens,
                    "required_tokens": required_tokens,
                    "available_tokens": available_tokens,
                },
            )
        return prompt.token_count

    @staticmethod
    def _validate_definition(definition: ModelDefinition, config: ModelLoadConfig) -> None:
        if not definition.enabled:
            raise InferenceError(
                code=InferenceErrorCode.INVALID_MODEL_DEFINITION,
                safe_message="The selected model is disabled in the registry.",
                model_key=definition.model_key,
            )
        backend_version = importlib.metadata.version("llama-cpp-python")
        if (
            definition.backend.backend_key != "llama_cpp"
            or definition.backend.required_version != backend_version
        ):
            raise InferenceError(
                code=InferenceErrorCode.BACKEND_UNAVAILABLE,
                safe_message="The required llama.cpp backend version is unavailable.",
                model_key=definition.model_key,
            )
        if config.context_size > definition.model.native_context_limit:
            raise InferenceError(
                code=InferenceErrorCode.INVALID_CONFIGURATION,
                safe_message="The configured context exceeds the model's native context limit.",
                model_key=definition.model_key,
                details={
                    "configured_context": config.context_size,
                    "native_context_limit": definition.model.native_context_limit,
                },
            )

    def _verify_artifact(
        self,
        definition: ModelDefinition,
    ) -> tuple[Path, str]:
        artifact_path = (self._model_root / definition.artifact.relative_path).resolve()
        if not artifact_path.is_relative_to(self._model_root):
            raise InferenceError(
                code=InferenceErrorCode.INVALID_MODEL_DEFINITION,
                safe_message="The model artifact path escapes the configured model root.",
                model_key=definition.model_key,
            )
        if not artifact_path.is_file():
            raise InferenceError(
                code=InferenceErrorCode.MODEL_NOT_FOUND,
                safe_message="The configured model artifact was not found.",
                model_key=definition.model_key,
            )
        actual_size = artifact_path.stat().st_size
        if actual_size != definition.artifact.size_bytes:
            raise InferenceError(
                code=InferenceErrorCode.MODEL_INTEGRITY_MISMATCH,
                safe_message="The model artifact size does not match the registry.",
                model_key=definition.model_key,
                details={
                    "expected_size": definition.artifact.size_bytes,
                    "actual_size": actual_size,
                },
            )
        digest = hashlib.sha512()
        with artifact_path.open("rb") as artifact_file:
            while chunk := artifact_file.read(8 * 1024 * 1024):
                digest.update(chunk)
        actual_digest = digest.hexdigest()
        if actual_digest != definition.artifact.sha512:
            raise InferenceError(
                code=InferenceErrorCode.MODEL_INTEGRITY_MISMATCH,
                safe_message="The model artifact digest does not match the registry.",
                model_key=definition.model_key,
            )
        return artifact_path, actual_digest

    @staticmethod
    def _build_runtime_info(
        definition: ModelDefinition,
        config: ModelLoadConfig,
        model: Llama,
        chat_template: LlamaCppChatTemplate,
        artifact_digest: str,
    ) -> ModelRuntimeInfo:
        architecture = model.metadata.get("general.architecture")
        if architecture != definition.model.architecture:
            raise InferenceError(
                code=InferenceErrorCode.MODEL_INTEGRITY_MISMATCH,
                safe_message="The loaded model architecture does not match the registry.",
                model_key=definition.model_key,
            )
        system_info = llama_cpp.llama_print_system_info().decode("utf-8", errors="replace")
        gpu_offload_supported = bool(llama_cpp.llama_supports_gpu_offload())
        build_variant = detect_llama_cpp_build_variant(
            system_info=system_info,
            gpu_offload_supported=gpu_offload_supported,
        )
        nvidia_process_memory = (
            observe_nvidia_process_gpu_memory()
            if build_variant == "cuda" and config.gpu_layers != 0
            else None
        )
        device_observation = detect_llama_cpp_device(
            system_info=system_info,
            gpu_offload_supported=gpu_offload_supported,
            gpu_layers=config.gpu_layers,
            nvidia_process_memory=nvidia_process_memory,
        )
        features = MODEL_REQUIRED_CAPABILITIES
        if device_observation.gpu_offload:
            features = features | {CapabilityFeature.GPU_OFFLOAD}
        capabilities = ModelCapabilities(
            features=features,
            native_context_limit=definition.model.native_context_limit,
            loaded_context_size=model.n_ctx(),
            max_concurrent_generations=1,
            # P5-CODEX-006 Rework (Codex Third Independent Review):
            # `TOOL` added so Retrieved/Untrusted RAG Reference content
            # can be spliced in under a genuinely distinct Role from
            # both `SYSTEM` (a real Instruction) and `USER` (a real
            # human turn) — see `ConversationGenerationService.
            # _inject_documentation_reference()`. `_prepare()` in
            # `chat_template.py` has no Role-specific branching of its
            # own; every `ChatMessage` (including `TOOL`) is dumped
            # generically and handed to the GGUF's own embedded Jinja
            # Chat Template, which is what actually decides how each
            # Role renders.
            supported_message_roles=frozenset(
                {MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT, MessageRole.TOOL}
            ),
        )
        return ModelRuntimeInfo(
            load_instance_id=str(uuid4()),
            model_key=definition.model_key,
            backend_key=definition.backend.backend_key,
            backend_version=definition.backend.required_version,
            backend_build_variant=device_observation.build_variant,
            model_architecture=architecture,
            format=definition.artifact.format,
            quantization=definition.artifact.quantization,
            artifact_size_bytes=definition.artifact.size_bytes,
            artifact_digest=ModelDigest(value=artifact_digest),
            artifact_digest_verified=True,
            definition_file_sha512=definition.definition_file_sha512,
            loaded_context_size=model.n_ctx(),
            effective_capabilities=capabilities,
            chat_template_source=chat_template.source,
            chat_template_digest=ModelDigest(value=chat_template.digest_sha512),
            device=device_observation.device,
            device_kind=device_observation.device_kind,
            acceleration_api=device_observation.acceleration_api,
            gpu_offload=device_observation.gpu_offload,
            gpu_offload_evidence=GpuOffloadEvidence(
                supported=device_observation.gpu_offload_supported,
                requested=device_observation.gpu_offload_requested,
                observed=device_observation.gpu_offload,
                observation_source=device_observation.observation_source,
                process_gpu_memory_bytes=device_observation.process_gpu_memory_bytes,
            ),
            warnings=chat_template.warnings,
        )
