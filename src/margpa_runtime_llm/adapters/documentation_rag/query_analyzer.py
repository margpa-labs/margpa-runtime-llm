"""Generic subject-signal analysis for natural-language lexical queries."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .lexical_tokenizer import JapaneseAwareLexicalTokenizer

_IDENTIFIER_SIGNAL_WEIGHT = 4.0
_AUXILIARY_SIGNAL_WEIGHT = 0.2


@dataclass(frozen=True, slots=True)
class LexicalQueryAnalysis:
    normalized_query: str
    weighted_terms: tuple[tuple[str, float], ...]
    identifier_tokens: tuple[str, ...]
    subject_identifiers: tuple[str, ...]


class GenericNaturalLanguageQueryAnalyzer:
    """Separate generic identifier subjects from auxiliary natural-language signals."""

    key = "generic_natural_language_subject_signal"
    version = "3"

    def __init__(self, tokenizer: JapaneseAwareLexicalTokenizer) -> None:
        self._tokenizer = tokenizer

    def analyze(self, value: str) -> LexicalQueryAnalysis:
        normalized = self._tokenizer.normalize(value)
        terms = Counter(self._tokenizer.tokenize(value))
        identifiers = tuple(dict.fromkeys(self._tokenizer.identifier_tokens(value)))
        subjects = tuple(dict.fromkeys(self._tokenizer.identifier_subject_tokens(value)))
        if not identifiers:
            return LexicalQueryAnalysis(
                normalized_query=normalized,
                weighted_terms=tuple(
                    (term, float(frequency)) for term, frequency in sorted(terms.items())
                ),
                identifier_tokens=(),
                subject_identifiers=(),
            )

        identifier_set = set(identifiers)
        weighted = {
            term: (
                _IDENTIFIER_SIGNAL_WEIGHT if term in identifier_set else _AUXILIARY_SIGNAL_WEIGHT
            )
            for term in terms
        }
        return LexicalQueryAnalysis(
            normalized_query=normalized,
            weighted_terms=tuple(sorted(weighted.items())),
            identifier_tokens=identifiers,
            subject_identifiers=subjects,
        )
