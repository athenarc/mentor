"""
Strict call wrapper for Gatekeeper managed-agent invocations.

Keeps gatekeeper as a managed agent, but enforces:
- a fixed short task template (no study JSON in task=)
- study/chunk/candidates payload only via additional_args['screening_payload']
- hard fail on classified provider errors (e.g. ContextOverflowError)
"""

from __future__ import annotations

import json
from typing import Any

from bastirr.errors import ContextOverflowError, classify_error


# Single additional_args key for all screening architectures.
GATEKEEPER_PAYLOAD_KEY = "screening_payload"

# Fixed short tasks — no study payloads.
GATEKEEPER_BATCH_TASK = (
    f"Title/abstract screen the studies in additional_args['{GATEKEEPER_PAYLOAD_KEY}'] "
    "against that payload's review protocol. Return one INCLUDE/EXCLUDE "
    "decision per study as JSON."
)

GATEKEEPER_SINGLE_STUDY_TASK = (
    f"Title/abstract screen the study in additional_args['{GATEKEEPER_PAYLOAD_KEY}'] "
    "against that payload's review protocol. Return exactly one INCLUDE/EXCLUDE "
    "decision as JSON."
)

GATEKEEPER_CHUNK_TASK = (
    f"Title/abstract screen the chunk in additional_args['{GATEKEEPER_PAYLOAD_KEY}'] "
    "against that payload's review protocol. Return one INCLUDE/EXCLUDE "
    "decision per chunk study as JSON."
)


def _is_study_record(value: Any) -> bool:
    """Match getter-tool study objects: study_index + title + abstract."""
    return (
        isinstance(value, dict)
        and "study_index" in value
        and "title" in value
        and "abstract" in value
    )


def _payload_looks_like_studies(value: Any) -> bool:
    """
    Accept getter-tool payloads (JSON str or already-parsed object):

    - batch / chunk: ``{"studies": [{"study_index", "title", "abstract"}, ...], ...}``
    - single-study: ``{"study": {"study_index", "title", "abstract"}, ...}``

    Indices-only objects (e.g. ``{"study_indices": [...]}``) fail.
    """
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return False
    if not isinstance(value, dict):
        return False
    studies = value.get("studies")
    if isinstance(studies, list) and studies and all(
        _is_study_record(item) for item in studies
    ):
        return True
    return _is_study_record(value.get("study"))


def _validate_additional_args(additional_args: dict | None) -> dict:
    if not isinstance(additional_args, dict) or not additional_args:
        raise ValueError(
            f"gatekeeper requires additional_args with payload key "
            f"'{GATEKEEPER_PAYLOAD_KEY}'."
        )
    if GATEKEEPER_PAYLOAD_KEY not in additional_args:
        raise ValueError(
            f"gatekeeper additional_args must include '{GATEKEEPER_PAYLOAD_KEY}' "
            f"(got keys: {sorted(additional_args.keys())})."
        )
    payload = additional_args[GATEKEEPER_PAYLOAD_KEY]
    if not _payload_looks_like_studies(payload):
        raise ValueError(
            f"gatekeeper additional_args['{GATEKEEPER_PAYLOAD_KEY}'] must be "
            "getter-tool JSON with a study record (study_index, title, abstract) "
            "or a non-empty studies list — not indices-only data."
        )
    return additional_args


class _StrictGatekeeperWrapper:
    """Proxy that keeps gatekeeper identity while enforcing call rules.

    ``agent(...)`` must be intercepted via a real type ``__call__`` (instance
    attribute assignment is ignored by Python's call protocol).

    Attribute reads fall through to the underlying agent (name, description,
    …). Writes such as ``inputs`` / ``output_type`` stay on this proxy, which
    is what smolagents registers as the managed agent.
    """

    def __init__(self, agent: Any, *, fixed_task: str) -> None:
        self._agent = agent
        self._fixed_task = fixed_task

    def __call__(
        self,
        task: str = "",
        additional_args: dict | None = None,
        **kwargs: Any,
    ) -> Any:
        _ = task
        validated_args = _validate_additional_args(additional_args)
        try:
            return self._agent(
                self._fixed_task,
                additional_args=validated_args,
                **kwargs,
            )
        except ContextOverflowError:
            raise
        except Exception as exc:
            classifier = classify_error(exc)
            if classifier is not None:
                raise classifier.exception_type(
                    f"Gatekeeper {classifier.name} while screening "
                    f"(payload_key={GATEKEEPER_PAYLOAD_KEY}): {exc}"
                ) from exc
            raise

    def __getattr__(self, name: str) -> Any:
        return getattr(self._agent, name)


def wrap_gatekeeper(
    agent: Any,
    *,
    fixed_task: str,
) -> Any:
    """
    Wrap a gatekeeper CodeAgent so managed calls use a fixed short task and
    require study payload only in ``additional_args['screening_payload']``.

    On classified hard failures (e.g. context overflow), raises the matching
    bastirr exception instead of returning a soft error string the
    orchestrator could recover from.

    Returns a thin proxy that still exposes the underlying managed-agent
    ``name`` / ``description`` (and other attributes) via delegation.
    """
    if isinstance(agent, _StrictGatekeeperWrapper):
        return agent
    return _StrictGatekeeperWrapper(agent, fixed_task=fixed_task)
