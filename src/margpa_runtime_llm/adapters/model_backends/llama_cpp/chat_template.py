"""GGUF Jinja chat-template and Qwen3 thinking control boundary."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any, cast

from llama_cpp import Llama, StoppingCriteriaList
from llama_cpp.llama_chat_format import Jinja2ChatFormatter

from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.runtime import InferenceWarning
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
from margpa_runtime_llm.modules.inference.domain.capabilities import CapabilityFeature
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)


@dataclass(frozen=True, slots=True)
class FormattedPrompt:
    prompt: str
    token_count: int


class LlamaCppChatTemplate:
    """Use the embedded template for both token counting and generation."""

    def __init__(self, model: Llama) -> None:
        template = model.metadata.get("tokenizer.chat_template")
        if not isinstance(template, str) or not template:
            raise InferenceError(
                code=InferenceErrorCode.UNSUPPORTED_CAPABILITY,
                safe_message="The model does not provide an embedded chat template.",
                details={"capability": CapabilityFeature.CHAT_TEMPLATE.value},
            )

        eos_token_id = model.token_eos()
        bos_token_id = model.token_bos()
        eos_token = model.detokenize([eos_token_id], special=True).decode("utf-8", errors="replace")
        bos_token = (
            model.detokenize([bos_token_id], special=True).decode("utf-8", errors="replace")
            if bos_token_id >= 0
            else ""
        )
        self._model = model
        self._template = template
        self._formatter = Jinja2ChatFormatter(
            template=template,
            eos_token=eos_token,
            bos_token=bos_token,
            stop_token_ids=[eos_token_id],
        )
        self._formatter_call = cast(Callable[..., Any], self._formatter)
        self._hard_switch_supported = "enable_thinking" in template
        self._prompt_normalization = self._build_prompt_normalization(eos_token)

    @property
    def source(self) -> str:
        return "gguf_metadata"

    @property
    def digest_sha512(self) -> str:
        return hashlib.sha512(self._template.encode("utf-8")).hexdigest()

    @property
    def hard_switch_supported(self) -> bool:
        return self._hard_switch_supported

    @staticmethod
    def _build_prompt_normalization(eos_token: str) -> tuple[tuple[str, str], ...]:
        """P6-CODEX-037 (Fifth Rework): some embedded chat templates hardcode
        a literal turn-separator string using the SentencePiece '▁' (U+2581)
        word-separator convention as plain Jinja text, instead of routing it
        through the template's own `{{ eos_token }}` variable. When that
        literal differs byte-for-byte from what this GGUF's own tokenizer
        emits for the real EOS token (verified here via a detokenize/
        tokenize round-trip on the exact artifact), every past-assistant-
        turn boundary in a multi-turn prompt silently degrades into ordinary
        sub-word tokens instead of the special EOS token, corrupting how the
        model reads conversation structure — this is the confirmed root
        cause of the DeepSeek multi-turn incompatibility. Model-agnostic: a
        template whose hardcoded literal already matches the tokenizer's own
        canonical bytes (e.g. Qwen, which uses `{{ eos_token }}` directly)
        produces no substitution pair here.
        """
        if " " not in eos_token:
            return ()
        underscore_variant = eos_token.replace(" ", "▁")
        if underscore_variant == eos_token:
            return ()
        return ((underscore_variant, eos_token),)

    def _normalize_rendered_prompt(self, prompt: str) -> str:
        for broken, canonical in self._prompt_normalization:
            prompt = prompt.replace(broken, canonical)
        return prompt

    @property
    def warnings(self) -> tuple[InferenceWarning, ...]:
        if self._hard_switch_supported:
            return ()
        return (
            InferenceWarning(
                code="thinking_soft_switch",
                safe_message="Thinking control uses the model's prompt-level soft switch.",
                capability=CapabilityFeature.THINKING_CONTROL,
            ),
        )

    def format_prompt(
        self,
        messages: tuple[ChatMessage, ...],
        thinking_mode: ThinkingMode,
    ) -> FormattedPrompt:
        native_messages, template_kwargs = self._prepare(messages, thinking_mode)
        try:
            formatted = self._formatter_call(messages=native_messages, **template_kwargs)
            prompt_text = self._normalize_rendered_prompt(formatted.prompt)
            tokens = self._model.tokenize(
                prompt_text.encode("utf-8"),
                add_bos=not formatted.added_special,
                special=True,
            )
            return FormattedPrompt(prompt=prompt_text, token_count=len(tokens))
        except InferenceError:
            raise
        except (TypeError, ValueError) as exc:
            raise InferenceError(
                code=InferenceErrorCode.BACKEND_PROTOCOL_ERROR,
                safe_message="The embedded chat template could not format the request.",
                details={"exception_type": type(exc).__name__},
            ) from exc

    def count_text_tokens(self, text: str) -> int:
        try:
            return len(
                self._model.tokenize(
                    text.encode("utf-8"),
                    add_bos=False,
                    special=True,
                )
            )
        except (TypeError, ValueError) as exc:
            raise InferenceError(
                code=InferenceErrorCode.BACKEND_PROTOCOL_ERROR,
                safe_message="The model tokenizer could not count text tokens.",
                details={"exception_type": type(exc).__name__},
            ) from exc

    def create_chat_completion(
        self,
        messages: tuple[ChatMessage, ...],
        parameters: GenerationParameters,
        *,
        stream: bool,
        cancellation: CancellationToken | None = None,
    ) -> object:
        """P6-CODEX-019 (Third Rework) / P6-CODEX-037 (Fifth Rework): renders
        the prompt manually against `Llama.create_completion()` instead of
        `Jinja2ChatFormatter.to_chat_handler()`'s opaque bridge, for two
        reasons that now both apply to every call, not only Background ones:

        1. The bridge does not expose a `stopping_criteria` pass-through, so
           a Background Model Call (Judge/Repair) could not be told to stop
           generating as soon as a Main Turn needs the shared Model.
        2. The bridge tokenizes the formatter's rendered prompt text
           unmodified, which for a template that hardcodes a turn-boundary
           literal not matching the tokenizer's own canonical byte sequence
           (see `_build_prompt_normalization`) silently breaks multi-turn
           EOS recognition. Normalizing the rendered prompt requires
           control over the render-then-tokenize step, which the opaque
           bridge does not offer.

        Tool/function-calling grammar derived from the Jinja chat
        formatter's own `result.stopping_criteria` is intentionally not
        applied here: this codebase never issues chat-format tool/function
        calls (only role-based prompt construction), so that omission has
        no observable effect.
        """
        native_messages, template_kwargs = self._prepare(messages, parameters.thinking_mode)
        formatted = self._formatter_call(messages=native_messages, **template_kwargs)
        prompt_text = self._normalize_rendered_prompt(formatted.prompt)
        tokens = self._model.tokenize(
            prompt_text.encode("utf-8"), add_bos=not formatted.added_special, special=True
        )
        stop = list(parameters.stop_sequences)
        if formatted.stop is not None:
            extra_stop = formatted.stop if isinstance(formatted.stop, list) else [formatted.stop]
            stop = [*stop, *extra_stop]
        stopping_criteria = (
            StoppingCriteriaList([lambda input_ids, logits: cancellation.is_cancelled()])
            if cancellation is not None
            else None
        )
        raw = self._model.create_completion(
            prompt=tokens,
            temperature=parameters.temperature,
            top_p=parameters.top_p,
            top_k=parameters.top_k,
            min_p=parameters.min_p,
            stream=stream,
            stop=stop,
            seed=parameters.seed,
            max_tokens=parameters.max_new_tokens,
            presence_penalty=parameters.presence_penalty,
            frequency_penalty=parameters.frequency_penalty,
            repeat_penalty=parameters.repeat_penalty,
            stopping_criteria=stopping_criteria,
        )
        if stream:
            return self._stream_completion_as_chat_deltas(cast(Iterator[dict[str, Any]], raw))
        completion = cast(dict[str, Any], raw)
        choice = cast(dict[str, Any], completion["choices"][0])
        return {
            "choices": [
                {
                    "message": {"role": "assistant", "content": choice.get("text", "")},
                    "finish_reason": choice.get("finish_reason"),
                }
            ],
            "usage": completion.get("usage"),
        }

    @staticmethod
    def _stream_completion_as_chat_deltas(
        chunks: Iterator[dict[str, Any]],
    ) -> Iterator[dict[str, Any]]:
        """Reshape `Llama.create_completion(stream=True)`'s raw completion
        chunks (`choices[0]["text"]`) into the OpenAI-chat delta shape
        (`choices[0]["delta"]["content"]`) that `LlamaCppGenerationStream`
        consumes — replicating what `Jinja2ChatFormatter.to_chat_handler()`'s
        bridge used to do, now that streaming also goes through the manual
        `create_completion()` call so prompt normalization applies to it too.
        """
        for chunk in chunks:
            choice = cast(dict[str, Any], chunk["choices"][0])
            finish_reason = choice.get("finish_reason")
            text = choice.get("text", "")
            yield {
                "choices": [
                    {
                        "delta": {} if finish_reason is not None else {"content": text},
                        "finish_reason": finish_reason,
                    }
                ]
            }

    def _prepare(
        self,
        messages: tuple[ChatMessage, ...],
        thinking_mode: ThinkingMode,
    ) -> tuple[list[Any], dict[str, object]]:
        prepared_messages = messages
        template_kwargs: dict[str, object] = {}
        if self._hard_switch_supported:
            if thinking_mode is ThinkingMode.DISABLED:
                template_kwargs["enable_thinking"] = False
            elif thinking_mode is ThinkingMode.ENABLED:
                template_kwargs["enable_thinking"] = True
        elif thinking_mode is not ThinkingMode.MODEL_DEFAULT:
            switch = "/think" if thinking_mode is ThinkingMode.ENABLED else "/no_think"
            prepared_messages = self._append_soft_switch(messages, switch)

        native_messages: list[Any] = [
            message.model_dump(mode="json", exclude_none=True) for message in prepared_messages
        ]
        return native_messages, template_kwargs

    @staticmethod
    def _append_soft_switch(
        messages: tuple[ChatMessage, ...],
        switch: str,
    ) -> tuple[ChatMessage, ...]:
        mutable = list(messages)
        for index in range(len(mutable) - 1, -1, -1):
            if mutable[index].role is MessageRole.USER:
                mutable[index] = mutable[index].model_copy(
                    update={"content": f"{mutable[index].content}\n{switch}"}
                )
                return tuple(mutable)
        raise InferenceError(
            code=InferenceErrorCode.INVALID_REQUEST,
            safe_message="Thinking control requires a user message.",
        )
