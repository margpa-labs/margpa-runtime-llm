"""Stable presentation surface for entrypoints and future user interfaces."""

from .application.thinking_presentation_service import (
    ThinkingPresentationService,
    ThinkingPresentationSession,
)
from .contracts.thinking import (
    DEFAULT_THINKING_DISPLAY_LABEL,
    NormalizedThinkingOutput,
    PresentationConfig,
    PresentedThinkingOutput,
    PresentedThinkingStreamDelta,
    PresentedThinkingStreamFinish,
    ResolvedThinkingPresentationPolicy,
    ThinkingContentKind,
    ThinkingParseStatus,
    ThinkingParseSummary,
    ThinkingParseWarning,
    ThinkingPersistence,
    ThinkingPresentationConfig,
    ThinkingPresentationSource,
    ThinkingSegmentDelta,
    ThinkingVisibility,
)

__all__ = [
    "DEFAULT_THINKING_DISPLAY_LABEL",
    "NormalizedThinkingOutput",
    "PresentationConfig",
    "PresentedThinkingOutput",
    "PresentedThinkingStreamDelta",
    "PresentedThinkingStreamFinish",
    "ResolvedThinkingPresentationPolicy",
    "ThinkingContentKind",
    "ThinkingParseStatus",
    "ThinkingParseSummary",
    "ThinkingParseWarning",
    "ThinkingPersistence",
    "ThinkingPresentationConfig",
    "ThinkingPresentationService",
    "ThinkingPresentationSession",
    "ThinkingPresentationSource",
    "ThinkingSegmentDelta",
    "ThinkingVisibility",
]
