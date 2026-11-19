"""
Strict call wrapper for Gatekeeper managed-agent invocations.

Keeps gatekeeper as a callable agent, but enforces:
- a fixed short task template (no study JSON in task=)
- study/batch payload only via additional_args['screening_payload']
- strict final-answer schema validation against the delegated studies
- hard fail on classified provider errors (e.g. ContextOverflowError)
"""

from __future__ import annotations

import ast
import json
from typing import Any

from mentor.errors import ContextOverflowError, classify_error
from mentor.tools.validation import validate_gatekeeper_answer


# Payload contract for screening (full, batch, or single-study payloads).
GATEKEEPER_PAYLOAD_KEY = "screening_payload"

# Fixed short task — no study payloads. The same task works for any batch size.
GATEKEEPER_TASK = (
    f"Title/abstract screen the studies in additional_args['{GATEKEEPER_PAYLOAD_KEY}'] "
    "against that payload's review protocol. Assess each criterion, call "
    "get_final_decision, and return INCLUDE/EXCLUDE/UNCLEAR JSON per study, "
    "preserving original study_index values."
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

    ``{"studies": [{"study_index", "title", "abstract"}, ...], ...}``

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
    return bool(
        isinstance(studies, list)
        and studies
        and all(_is_study_record(item) for item in studies)
    )


def _parse_payload(value: Any) -> dict:
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"gatekeeper additional_args['{GATEKEEPER_PAYLOAD_KEY}'] "
                "is not valid JSON."
            ) from exc
    elif isinstance(value, dict):
        parsed = value
    else:
        raise ValueError(
            f"gatekeeper additional_args['{GATEKEEPER_PAYLOAD_KEY}'] must be "
            "a JSON object or JSON string."
        )
    if not isinstance(parsed, dict):
        raise ValueError(
            f"gatekeeper additional_args['{GATEKEEPER_PAYLOAD_KEY}'] JSON root "
            "must be an object."
        )
    return parsed


def _delegated_studies(payload: Any) -> list[dict[str, Any]]:
    parsed = _parse_payload(payload)
    studies = parsed.get("studies")
    if not isinstance(studies, list) or not studies:
        raise ValueError(
            f"gatekeeper additional_args['{GATEKEEPER_PAYLOAD_KEY}'] has no "
            "non-empty studies list."
        )
    return studies


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
            "getter-tool JSON with a non-empty studies list of records "
            "(study_index, title, abstract) — not indices-only data."
        )
    return additional_args


def _agent_answer_payload(result: Any) -> Any:
    """Unwrap a CodeAgent run result to the raw final-answer value."""
    if result is None:
        return ""
    if isinstance(result, (str, dict)):
        return result
    output = getattr(result, "output", None)
    if output is not None:
        return output
    return result


def coerce_gatekeeper_answer_json(result: Any) -> str:
    """
    Normalize a Gatekeeper final answer to a JSON object string.

    CodeAgents often call ``final_answer({...})`` (Python dict) or return
    ``str(dict)`` with single quotes. Validation and persistence expect
    strict JSON, so coerce dict / Python-literal strings before checking.
    """
    value = _agent_answer_payload(result)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    if not isinstance(value, str):
        value = str(value)
    text = value.strip()
    if not text:
        return ""
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass
    try:
        parsed = ast.literal_eval(text)
    except (SyntaxError, ValueError, MemoryError):
        return text
    if isinstance(parsed, dict):
        return json.dumps(parsed, ensure_ascii=False)
    return text


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
        studies = _delegated_studies(validated_args[GATEKEEPER_PAYLOAD_KEY])
        try:
            # Call run() directly so we validate the raw final answer (not the
            # managed-agent report wrapper) before returning to the Orchestrator.
            result = self._agent.run(
                self._fixed_task,
                additional_args=validated_args,
                reset=kwargs.get("reset", True),
                stream=kwargs.get("stream", False),
                max_steps=kwargs.get("max_steps"),
                return_full_result=kwargs.get("return_full_result"),
            )
            answer = coerce_gatekeeper_answer_json(result)
            if not kwargs.get("stream"):
                validate_gatekeeper_answer(answer, studies)
            return answer
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
    fixed_task: str = GATEKEEPER_TASK,
) -> Any:
    """
    Wrap a gatekeeper CodeAgent so managed calls use a fixed short task and
    require study payload only in ``additional_args['screening_payload']``.

    Each call validates the final answer against the delegated studies in the
    payload (schema, indices, titles, counts; rejects duplicate JSON keys and
    NaN/Infinity).

    On classified hard failures (e.g. context overflow), raises the matching
    mentor exception instead of returning a soft error string the
    orchestrator could recover from.

    Returns a thin proxy that still exposes the underlying managed-agent
    ``name`` / ``description`` (and other attributes) via delegation.
    """
    if isinstance(agent, _StrictGatekeeperWrapper):
        return agent
    return _StrictGatekeeperWrapper(agent, fixed_task=fixed_task)
