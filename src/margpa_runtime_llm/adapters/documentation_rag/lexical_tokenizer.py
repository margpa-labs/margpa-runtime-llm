"""Unicode-normalized Japanese n-gram and Latin identifier tokenization."""

from __future__ import annotations

import re
import unicodedata

_LATIN_TOKEN = re.compile(r"[a-z0-9_./-]+")
_SURFACE_LATIN_TOKEN = re.compile(r"[A-Za-z0-9_./-]+")
_JAPANESE_RUN = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+")
_WHITESPACE = re.compile(r"\s+")


class JapaneseAwareLexicalTokenizer:
    key = "unicode_japanese_ngram"
    version = "2"

    def normalize(self, value: str) -> str:
        return _WHITESPACE.sub(" ", unicodedata.normalize("NFKC", value).casefold()).strip()

    def tokenize(self, value: str) -> tuple[str, ...]:
        normalized = self.normalize(value)
        tokens = list(_identifier_tokens(normalized))
        for match in _JAPANESE_RUN.finditer(normalized):
            run = match.group(0)
            if len(run) == 1:
                tokens.append(run)
                continue
            for size in (2, 3):
                tokens.extend(run[index : index + size] for index in range(len(run) - size + 1))
        return tuple(tokens)

    def identifier_tokens(self, value: str) -> tuple[str, ...]:
        """Return generic Latin, numeric, path, and code identifier signals."""

        return _identifier_tokens(self.normalize(value))

    def identifier_subject_tokens(self, value: str) -> tuple[str, ...]:
        """Return generic high-signal subjects while preserving prose as lexical terms."""

        surface = unicodedata.normalize("NFKC", value)
        subjects: list[str] = []
        for match in _SURFACE_LATIN_TOKEN.finditer(surface):
            token = match.group(0).strip(".")
            if token and _is_high_signal_identifier(token):
                subjects.append(self.normalize(token))
        return tuple(subjects)


def _identifier_tokens(normalized: str) -> tuple[str, ...]:
    tokens: list[str] = []
    for match in _LATIN_TOKEN.finditer(normalized):
        token = match.group(0)
        tokens.append(token)
        for component in re.split(r"[./_-]+", token):
            if component and component != token:
                tokens.append(component)
    return tuple(tokens)


def _is_high_signal_identifier(token: str) -> bool:
    letters = tuple(character for character in token if character.isascii() and character.isalpha())
    if not letters:
        return False
    if len(letters) >= 2 and all(character.isupper() for character in letters):
        return True
    if any(character.isdigit() for character in token):
        return True
    if re.search(r"[A-Za-z0-9][_.\/-][A-Za-z0-9]", token):
        return True
    return any(character.islower() for character in letters) and any(
        character.isupper() for character in token[1:]
    )
