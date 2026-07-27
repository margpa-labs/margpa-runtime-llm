"""Lifecycle states owned by a single Model Port instance."""

from enum import StrEnum


class ModelLifecycleState(StrEnum):
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    GENERATING = "generating"
    UNLOADING = "unloading"
    FAILED = "failed"
