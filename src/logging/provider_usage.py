"""
Per-run provider usage collection.

Cost and provider-routing data are not exposed by any mentor/smolagents
API today, but they already survive, untouched, on the raw completion
object smolagents attaches to every ``ActionStep`` (``step.model_output_message
.raw``) — OpenAI-compatible response models allow unknown extra fields, so
whatever a provider adds (e.g. OpenRouter's ``usage.cost`` and top-level
``openrouter_metadata``) is preserved.
"""

from __future__ import annotations

from typing import Any


def _response_field(obj: Any, name: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, (getattr(obj, "model_extra", None) or {}).get(name))


def extract_call_usage(raw: Any) -> dict:
    """Pull provider cost/routing data off one raw completion response."""
    usage = _response_field(raw, "usage")
    routing_metadata = _response_field(raw, "openrouter_metadata")
    return {
        "cost": _response_field(usage, "cost"),
        "provider": _response_field(raw, "provider") or _response_field(routing_metadata, "provider_name"),
        "routing_metadata": routing_metadata,
    }


def raw_completion_from_step(step: Any) -> Any:
    """Safely read ``step.model_output_message.raw`` when present."""
    message = getattr(step, "model_output_message", None)
    if message is None:
        return None
    return getattr(message, "raw", None)


class ProviderUsageCollector:
    """Smolagents ``ActionStep`` callback that accumulates provider usage."""

    def __init__(self) -> None:
        self._calls: list[dict] = []

    def on_action_step(self, step, agent=None, **kwargs) -> None:
        raw = raw_completion_from_step(step)
        if raw is None:
            return
        self._calls.append(extract_call_usage(raw))

    def summary(self) -> dict:
        """Aggregate collected calls into the run-level usage fields."""
        costs = [call["cost"] for call in self._calls if call.get("cost") is not None]
        routing = [
            call["routing_metadata"] for call in self._calls if call.get("routing_metadata")
        ]
        return {
            "cost": sum(costs) if costs else None,
            "additional_metadata": {"routing_metadata": routing} if routing else {},
        }


def attach_usage_collector(step_callbacks: dict, collector: ProviderUsageCollector) -> dict:
    """Return a copy of *step_callbacks* with the collector added for ActionStep."""
    from smolagents import ActionStep

    existing = step_callbacks.get(ActionStep, [])
    if not isinstance(existing, list):
        existing = [existing]
    return {**step_callbacks, ActionStep: [*existing, collector.on_action_step]}
