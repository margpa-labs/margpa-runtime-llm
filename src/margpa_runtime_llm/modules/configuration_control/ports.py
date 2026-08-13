"""Replaceable typed descriptor ports for configuration control."""

from typing import Protocol, runtime_checkable

from .contracts import FeatureHookDescriptor, RecordingHookDescriptor


@runtime_checkable
class FeatureHookDescriptorPort(Protocol):
    def descriptor(self) -> FeatureHookDescriptor: ...


@runtime_checkable
class RecordingHookDescriptorPort(Protocol):
    def descriptor(self) -> RecordingHookDescriptor: ...
