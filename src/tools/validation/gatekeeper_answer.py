"""Validate Gatekeeper screening answer JSON against delegated studies."""

from __future__ import annotations

import json
from typing import Any


_ROOT_ATTRIBUTES = (
    "n_total",
    "n_included",
    "n_excluded",
    "decisions",
)
_DECISION_ATTRIBUTES = (
    "study_index",
    "title",
    "decision",
    "confidence",
    "rationale",
)
_VALID_DECISIONS = {"INCLUDE", "EXCLUDE"}
_VALID_CONFIDENCE_VALUES = {"high", "medium", "low"}


class _DuplicateJsonAttributeError(ValueError):
    """Raised when a JSON object contains the same attribute more than once."""


class _InvalidJsonConstantError(ValueError):
    """Raised for non-standard JSON constants such as NaN and Infinity."""


def _json_object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonAttributeError(
                f"Duplicate JSON object attribute {key!r}."
            )
        result[key] = value
    return result


def _reject_invalid_json_constant(value: str) -> None:
    raise _InvalidJsonConstantError(f"Invalid JSON constant {value!r}.")


def _attribute_errors(
    value: dict[str, Any],
    expected_attributes: tuple[str, ...],
    *,
    location: str,
) -> list[str]:
    actual = set(value)
    errors: list[str] = []
    missing = [name for name in expected_attributes if name not in actual]
    unexpected = sorted(actual - set(expected_attributes))
    if missing:
        errors.append(
            f"Missing {location} attributes: {missing}. "
            f"Expected exactly {list(expected_attributes)}."
        )
    if unexpected:
        errors.append(
            f"Unexpected {location} attributes: {unexpected}. "
            f"Expected exactly {list(expected_attributes)}."
        )
    return errors


def _studies_by_index(delegated_studies: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    if not isinstance(delegated_studies, list) or not delegated_studies:
        raise ValueError(
            "Invalid delegated studies configuration: expected a non-empty list."
        )

    configuration_errors: list[str] = []
    studies_by_index: dict[int, dict[str, Any]] = {}
    for position, study in enumerate(delegated_studies, start=1):
        if not isinstance(study, dict):
            configuration_errors.append(
                f"Delegated study at position {position} is not an object."
            )
            continue

        missing = [
            attribute
            for attribute in ("study_index", "title", "abstract")
            if attribute not in study
        ]
        if missing:
            configuration_errors.append(
                f"Delegated study at position {position} is missing attributes: {missing}."
            )
            continue

        study_index = study["study_index"]
        title = study["title"]
        abstract = study["abstract"]
        if type(study_index) is not int or study_index < 1:
            configuration_errors.append(
                f"Delegated study at position {position} has invalid study_index "
                f"{study_index!r}; expected a positive integer."
            )
            continue
        if study_index in studies_by_index:
            configuration_errors.append(
                f"Delegated studies contain duplicate study_index {study_index}."
            )
            continue
        if not isinstance(title, str):
            configuration_errors.append(
                f"Delegated study {study_index} has a non-string title."
            )
            continue
        if not isinstance(abstract, str):
            configuration_errors.append(
                f"Delegated study {study_index} has a non-string abstract."
            )
            continue

        studies_by_index[study_index] = {
            "study_index": study_index,
            "title": title,
            "abstract": abstract,
        }

    if configuration_errors:
        raise ValueError(
            "Invalid delegated studies configuration:\n- "
            + "\n- ".join(configuration_errors)
        )
    return studies_by_index


def _raise_validation_errors(errors: list[str]) -> None:
    if errors:
        raise ValueError(
            "Gatekeeper final answer validation failed:\n- " + "\n- ".join(errors)
        )


def validate_gatekeeper_answer(
    final_answer: Any,
    delegated_studies: list[dict[str, Any]],
) -> bool:
    """
    Validate a Gatekeeper answer against its exact delegated study set.

    Raises ``ValueError`` with a detailed message on failure; returns ``True``
    when the answer is complete and valid. Rejects duplicate JSON object keys
    and non-standard constants (``NaN``, ``Infinity``).
    """
    studies = _studies_by_index(delegated_studies)

    if not isinstance(final_answer, str):
        raise ValueError(
            "Gatekeeper final answer is not a JSON string. "
            f"Received type {type(final_answer).__name__}."
        )

    try:
        payload = json.loads(
            final_answer,
            object_pairs_hook=_json_object_without_duplicates,
            parse_constant=_reject_invalid_json_constant,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Gatekeeper final answer is not valid JSON. "
            f"JSON error at line {exc.lineno}, column {exc.colno}: {exc.msg}."
        ) from exc
    except _DuplicateJsonAttributeError as exc:
        raise ValueError(
            f"Gatekeeper final answer contains a duplicate JSON attribute. {exc}"
        ) from exc
    except _InvalidJsonConstantError as exc:
        raise ValueError(f"Gatekeeper final answer is not valid JSON. {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError(
            "Gatekeeper final answer JSON root is not an object. "
            f"Received {type(payload).__name__}."
        )

    errors = _attribute_errors(payload, _ROOT_ATTRIBUTES, location="root")
    expected_total = len(studies)

    counts: dict[str, int] = {}
    for attribute in ("n_total", "n_included", "n_excluded"):
        if attribute not in payload:
            continue
        value = payload[attribute]
        if type(value) is not int:
            errors.append(
                f"Invalid type for {attribute}: {type(value).__name__}. "
                "Expected an integer."
            )
            continue
        counts[attribute] = value

    n_total = counts.get("n_total")
    n_included = counts.get("n_included")
    n_excluded = counts.get("n_excluded")
    if n_total is not None:
        if n_total < 1:
            errors.append(
                f"Invalid value for n_total: {n_total}. Expected a positive integer."
            )
        if n_total != expected_total:
            errors.append(
                f"Invalid value for n_total: {n_total}. "
                f"The delegated study count is {expected_total}."
            )
    for attribute, value in (
        ("n_included", n_included),
        ("n_excluded", n_excluded),
    ):
        if value is not None and value < 0:
            errors.append(
                f"Invalid value for {attribute}: {value}. "
                "Expected a nonnegative integer."
            )
    if n_total is not None and n_included is not None and n_excluded is not None:
        if n_included + n_excluded != n_total:
            errors.append(
                f"Inconsistent summary counts: n_included ({n_included}) + "
                f"n_excluded ({n_excluded}) is {n_included + n_excluded}, "
                f"while n_total is {n_total}."
            )

    decisions = payload.get("decisions")
    if not isinstance(decisions, list):
        if "decisions" in payload:
            errors.append(
                f"Invalid type for decisions: {type(decisions).__name__}. "
                "Expected a list."
            )
        _raise_validation_errors(errors)
        return True

    if len(decisions) != expected_total:
        errors.append(
            f"Invalid decisions list size: {len(decisions)}. "
            f"The delegated study count is {expected_total}."
        )
    if n_total is not None and len(decisions) != n_total:
        errors.append(
            f"The decisions list contains {len(decisions)} entries, "
            f"while n_total is {n_total}."
        )

    returned_indices: set[int] = set()
    include_count = 0
    exclude_count = 0
    for position, decision_record in enumerate(decisions, start=1):
        location = f"decision at position {position}"
        if not isinstance(decision_record, dict):
            errors.append(
                f"The {location} is not an object; received "
                f"{type(decision_record).__name__}."
            )
            continue

        errors.extend(
            _attribute_errors(
                decision_record,
                _DECISION_ATTRIBUTES,
                location=location,
            )
        )

        study_index = decision_record.get("study_index")
        valid_index = type(study_index) is int and study_index > 0
        if not valid_index:
            if "study_index" in decision_record:
                errors.append(
                    f"Invalid study_index {study_index!r} in the {location}. "
                    "Expected a positive integer."
                )
        else:
            if study_index in returned_indices:
                errors.append(f"Duplicate decision for study_index {study_index}.")
            returned_indices.add(study_index)
            if study_index not in studies:
                errors.append(
                    f"Unexpected study_index {study_index}. "
                    f"Delegated study indices are {sorted(studies)}."
                )

        title = decision_record.get("title")
        if "title" in decision_record and not isinstance(title, str):
            errors.append(
                f"Invalid title type in the {location}: "
                f"{type(title).__name__}. Expected a string."
            )
        elif (
            isinstance(title, str)
            and valid_index
            and study_index in studies
        ):
            expected_title = studies[study_index]["title"]
            if title.lower().strip() != expected_title.lower().strip():
                errors.append(
                    f"Title mismatch for study_index {study_index}. "
                    f"Received {title!r}; delegated title is {expected_title!r}."
                )

        decision = decision_record.get("decision")
        if "decision" in decision_record:
            if not isinstance(decision, str):
                errors.append(
                    f"Invalid decision type in the {location}: "
                    f"{type(decision).__name__}. Expected a string."
                )
            elif decision not in _VALID_DECISIONS:
                errors.append(
                    f"Invalid decision value {decision!r} in the {location}. "
                    "Expected 'INCLUDE' or 'EXCLUDE'."
                )
            elif decision == "INCLUDE":
                include_count += 1
            else:
                exclude_count += 1

        confidence = decision_record.get("confidence")
        if "confidence" in decision_record:
            if not isinstance(confidence, str):
                errors.append(
                    f"Invalid confidence type in the {location}: "
                    f"{type(confidence).__name__}. Expected a string."
                )
            elif confidence not in _VALID_CONFIDENCE_VALUES:
                errors.append(
                    f"Invalid confidence value {confidence!r} in the {location}. "
                    "Expected 'high', 'medium', or 'low'."
                )

        rationale = decision_record.get("rationale")
        if "rationale" in decision_record and not isinstance(rationale, str):
            errors.append(
                f"Invalid rationale type in the {location}: "
                f"{type(rationale).__name__}. Expected a string."
            )

    expected_indices = set(studies)
    missing_indices = sorted(expected_indices - returned_indices)
    unexpected_indices = sorted(returned_indices - expected_indices)
    if missing_indices:
        errors.append(
            f"Missing decisions for delegated study indices: {missing_indices}."
        )
    if unexpected_indices:
        errors.append(
            f"Decisions contain undelegated study indices: {unexpected_indices}."
        )
    if n_included is not None and n_included != include_count:
        errors.append(
            f"n_included is {n_included}, while the decisions list contains "
            f"{include_count} INCLUDE decisions."
        )
    if n_excluded is not None and n_excluded != exclude_count:
        errors.append(
            f"n_excluded is {n_excluded}, while the decisions list contains "
            f"{exclude_count} EXCLUDE decisions."
        )

    _raise_validation_errors(errors)
    return True
