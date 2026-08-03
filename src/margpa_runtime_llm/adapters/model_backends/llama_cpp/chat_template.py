"""GGUF Jinja chat-template and Qwen3 thinking control boundary."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

from llama_cpp import Llama
from llama_cpp.llama_chat_format import Jinja2ChatFormatter

from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.runtime import InferenceWarning
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
        self._handler = cast(Callable[..., Any], self._formatter.to_chat_handler())
        self._hard_switch_supported = "enable_thinking" in template

    @property
    def source(self) -> str:
        return "gguf_metadata"

    @property
    def digest_sha512(self) -> str:
        return hashlib.sha512(self._template.encode("utf-8")).hexdigest()

    @property
    def hard_switch_supported(self) -> bool:
        return self._hard_switch_supported

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
            tokens = self._model.tokenize(
                formatted.prompt.encode("utf-8"),
                add_bos=not formatted.added_special,
                special=True,
            )
            return FormattedPrompt(prompt=formatted.prompt, token_count=len(tokens))
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
    ) -> object:
        native_messages, template_kwargs = self._prepare(messages, parameters.thinking_mode)
        return self._handler(
            llama=self._model,
            messages=native_messages,
            temperature=parameters.temperature,
            top_p=parameters.top_p,
            top_k=parameters.top_k,
            min_p=parameters.min_p,
            stream=stream,
            stop=list(parameters.stop_sequences),
            seed=parameters.seed,
            max_tokens=parameters.max_new_tokens,
            presence_penalty=parameters.presence_penalty,
            frequency_penalty=parameters.frequency_penalty,
            repeat_penalty=parameters.repeat_penalty,
            **template_kwargs,
        )

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
