"""Composition root for compatible sparse documentation RAG adapter graphs."""

from __future__ import annotations

import hashlib
import json
import threading
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ValidationError

from margpa_runtime_llm.adapters.documentation_rag import (
    Bm25DocumentationRetriever,
    BoundedDocumentationContextAssembler,
    CompositeDocumentSource,
    DeterministicMarkdownChunker,
    ExplicitMarkdownDocumentSource,
    InMemoryLexicalIndexStore,
    LocalCorpusDocumentSource,
    LocalMarkdownDocumentSource,
    SystemCitationAdapter,
)
from margpa_runtime_llm.adapters.documentation_rag.lexical_tokenizer import (
    JapaneseAwareLexicalTokenizer,
)
from margpa_runtime_llm.modules.documentation_rag.application import (
    DocumentationRagApplicationService,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DOCUMENTATION_RAG_CITATION_SOURCE_CLASS,
    DocumentationRagDefaultsConfig,
    DocumentationRagFeatureConfig,
    DocumentationRagPlatform,
    LightningPublicDocumentationRagFeatureConfig,
    LocalDocumentationRagFeatureConfig,
)
from margpa_runtime_llm.modules.documentation_rag.local_corpus_contracts import (
    LOCAL_CORPUS_SOURCE_CLASS,
)
from margpa_runtime_llm.modules.documentation_rag.local_corpus_ports import (
    LocalCorpusRegistryPort,
)
from margpa_runtime_llm.modules.documentation_rag.ports import (
    ContextualRagOrchestratorPort,
    DocumentSourcePort,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)

TextTokenCounter = Callable[[str], int]


class _DeferredTextTokenCounter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counter: TextTokenCounter | None = None

    def bind(self, counter: TextTokenCounter) -> None:
        with self._lock:
            self._counter = counter

    def __call__(self, text: str) -> int:
        with self._lock:
            counter = self._counter
        if counter is None:
            raise RuntimeError("the model token counter is not bound")
        return counter(text)


@dataclass(frozen=True, slots=True)
class DocumentationRagComposition:
    orchestrator: ContextualRagOrchestratorPort
    defaults: DocumentationRagDefaultsConfig
    feature: DocumentationRagFeatureConfig
    _token_counter: _DeferredTextTokenCounter

    def bind_token_counter(self, counter: TextTokenCounter) -> None:
        self._token_counter.bind(counter)


LocalDocumentationRagComposition = DocumentationRagComposition


def build_documentation_rag(
    *,
    project_root: Path,
    defaults_path: Path,
    feature_path: Path,
    access_mode: str,
    platform_observation: str,
    local_corpus_registry: LocalCorpusRegistryPort | None = None,
) -> DocumentationRagComposition:
    defaults = _load_toml_model(defaults_path, DocumentationRagDefaultsConfig)
    feature = _load_feature_profile(feature_path)
    source: DocumentSourcePort
    if isinstance(feature, LocalDocumentationRagFeatureConfig):
        if access_mode != "local" or platform_observation != DocumentationRagPlatform.MACOS_ARM64:
            raise _invalid_configuration()
        source = LocalMarkdownDocumentSource(
            project_root=project_root,
            feature=feature,
        )
        # Phase 7 (P7-B): the mutable Local Corpus is composed in only for
        # the real local developer runtime (`access_mode == "local"`) — the
        # Lightning public container profile below has no writable per-user
        # storage guarantee and stays exactly Phase 2 behavior.
        if local_corpus_registry is not None:
            source = CompositeDocumentSource(
                sources_by_class={
                    DOCUMENTATION_RAG_CITATION_SOURCE_CLASS: source,
                    LOCAL_CORPUS_SOURCE_CLASS: LocalCorpusDocumentSource(
                        registry=local_corpus_registry,
                        project_root=project_root,
                    ),
                }
            )
    else:
        if (
            access_mode not in feature.allowed_access_modes
            or platform_observation not in feature.allowed_platforms
        ):
            raise _invalid_configuration()
        source = ExplicitMarkdownDocumentSource(
            project_root=project_root,
            feature=feature,
        )

    return _compose_documentation_rag(
        defaults=defaults,
        feature=feature,
        source=source,
    )


def build_local_documentation_rag(
    *,
    project_root: Path,
    defaults_path: Path,
    feature_path: Path,
    local_corpus_registry: LocalCorpusRegistryPort | None = None,
) -> LocalDocumentationRagComposition:
    return build_documentation_rag(
        project_root=project_root,
        defaults_path=defaults_path,
        feature_path=feature_path,
        access_mode="local",
        platform_observation=DocumentationRagPlatform.MACOS_ARM64,
        local_corpus_registry=local_corpus_registry,
    )


def _compose_documentation_rag(
    *,
    defaults: DocumentationRagDefaultsConfig,
    feature: DocumentationRagFeatureConfig,
    source: DocumentSourcePort,
) -> DocumentationRagComposition:
    tokenizer = JapaneseAwareLexicalTokenizer()
    retriever = Bm25DocumentationRetriever(
        tokenizer=tokenizer,
        config=feature.retrieval,
    )
    profile_digest = hashlib.sha512(
        json.dumps(
            feature.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    token_counter = _DeferredTextTokenCounter()
    orchestrator = DocumentationRagApplicationService(
        source=source,
        chunker=DeterministicMarkdownChunker(feature.chunking),
        index_store=InMemoryLexicalIndexStore(),
        retriever=retriever,
        context_assembler=BoundedDocumentationContextAssembler(
            token_counter=token_counter,
        ),
        citation=SystemCitationAdapter(),
        retrieval_config=feature.retrieval,
        context_budget=feature.context.as_budget(),
        profile_digest=profile_digest,
        max_chunks=feature.limits.max_chunks,
    )
    return DocumentationRagComposition(
        orchestrator=orchestrator,
        defaults=defaults,
        feature=feature,
        _token_counter=token_counter,
    )


def _load_feature_profile(path: Path) -> DocumentationRagFeatureConfig:
    try:
        with path.open("rb") as config_file:
            data = tomllib.load(config_file)
        schema_version = data.get("schema_version")
        if schema_version == "1":
            return LocalDocumentationRagFeatureConfig.model_validate(data)
        if schema_version == "2":
            return LightningPublicDocumentationRagFeatureConfig.model_validate(data)
        raise ValueError("unsupported documentation RAG feature schema")
    except (
        FileNotFoundError,
        OSError,
        tomllib.TOMLDecodeError,
        ValidationError,
        ValueError,
    ) as exc:
        raise _invalid_configuration(type(exc).__name__) from exc


def _invalid_configuration(exception_type: str | None = None) -> InferenceError:
    details = {"exception_type": exception_type} if exception_type is not None else None
    return InferenceError(
        code=InferenceErrorCode.INVALID_CONFIGURATION,
        safe_message="The documentation RAG configuration is invalid.",
        details=details,
    )


def _load_toml_model[ConfigType: BaseModel](
    path: Path,
    model_type: type[ConfigType],
) -> ConfigType:
    try:
        with path.open("rb") as config_file:
            data = tomllib.load(config_file)
        return model_type.model_validate(data)
    except (
        FileNotFoundError,
        OSError,
        tomllib.TOMLDecodeError,
        ValidationError,
    ) as exc:
        raise _invalid_configuration(type(exc).__name__) from exc
