"""Validate Gatekeeper screening answer JSON against delegated studies."""

from __future__ import annotations

import json
from typing import Any

from mentor.tools.screening_tools import compute_final_decision


_ROOT_ATTRIBUTES = (
    "n_total",
    "n_included",
    "n_excluded",
    "n_unclear",
    "decisions",
)
_DECISION_ATTRIBUTES = (
    "study_index",
    "criteria",
    "final_decision",
)
_CRITERION_ATTRIBUTES = (
    "id",
    "label",
    "rationale",
)
_VALID_FINAL_DECISIONS = {"INCLUDE", "EXCLUDE", "UNCLEAR"}
_INCLUSION_LABELS = {"MET", "NOT_MET", "UNCLEAR"}
_EXCLUSION_LABELS = {"TRIGGERED", "NOT_TRIGGERED", "UNCLEAR"}


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


def _criterion_label_errors(
    criterion: dict[str, Any],
    *,
    location: str,
) -> list[str]:
    errors: list[str] = []
    errors.extend(
        _attribute_errors(criterion, _CRITERION_ATTRIBUTES, location=location)
    )
    criterion_id = criterion.get("id")
    label = criterion.get("label")
    rationale = criterion.get("rationale")
    if "id" in criterion and not isinstance(criterion_id, str):
        errors.append(f"Invalid id type in the {location}: expected a string.")
        return errors
    if "rationale" in criterion and not isinstance(rationale, str):
        errors.append(
            f"Invalid rationale type in the {location}: expected a string."
        )
    if "rationale" in criterion and isinstance(rationale, str) and not rationale.strip():
        errors.append(f"Empty rationale in the {location}.")
    if "label" in criterion and not isinstance(label, str):
        errors.append(f"Invalid label type in the {location}: expected a string.")
        return errors
    if not isinstance(label, str):
        return errors

    label_upper = label.upper()
    id_upper = str(criterion_id or "").strip().upper()
    if id_upper.startswith("IC"):
        if label_upper not in _INCLUSION_LABELS:
            errors.append(
                f"Invalid inclusion label {label!r} in the {location}. "
                "Expected MET, NOT_MET, or UNCLEAR."
            )
    elif id_upper.startswith("EC"):
        if label_upper not in _EXCLUSION_LABELS:
            errors.append(
                f"Invalid exclusion label {label!r} in the {location}. "
                "Expected TRIGGERED, NOT_TRIGGERED, or UNCLEAR."
            )
    else:
        errors.append(
            f"Invalid criterion id {criterion_id!r} in the {location}; "
            "expected an id starting with IC or EC."
        )
    return errors


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
    for attribute in ("n_total", "n_included", "n_excluded", "n_unclear"):
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
    n_unclear = counts.get("n_unclear")
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
        ("n_unclear", n_unclear),
    ):
        if value is not None and value < 0:
            errors.append(
                f"Invalid value for {attribute}: {value}. "
                "Expected a nonnegative integer."
            )
    if (
        n_total is not None
        and n_included is not None
        and n_excluded is not None
        and n_unclear is not None
    ):
        if n_included + n_excluded + n_unclear != n_total:
            errors.append(
                f"Inconsistent summary counts: n_included ({n_included}) + "
                f"n_excluded ({n_excluded}) + n_unclear ({n_unclear}) is "
                f"{n_included + n_excluded + n_unclear}, while n_total is {n_total}."
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
    unclear_count = 0
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

        criteria = decision_record.get("criteria")
        if "criteria" in decision_record and not isinstance(criteria, list):
            errors.append(
                f"Invalid criteria type in the {location}: "
                f"{type(criteria).__name__}. Expected a list."
            )
            criteria = None
        elif isinstance(criteria, list):
            if not criteria:
                errors.append(f"Empty criteria list in the {location}.")
            for c_pos, criterion in enumerate(criteria, start=1):
                c_location = f"{location} criterion at position {c_pos}"
                if not isinstance(criterion, dict):
                    errors.append(
                        f"The {c_location} is not an object; received "
                        f"{type(criterion).__name__}."
                    )
                    continue
                errors.extend(_criterion_label_errors(criterion, location=c_location))

        final_decision = decision_record.get("final_decision")
        if "final_decision" in decision_record:
            if not isinstance(final_decision, str):
                errors.append(
                    f"Invalid final_decision type in the {location}: "
                    f"{type(final_decision).__name__}. Expected a string."
                )
            elif final_decision not in _VALID_FINAL_DECISIONS:
                errors.append(
                    f"Invalid final_decision value {final_decision!r} in the "
                    f"{location}. Expected INCLUDE, EXCLUDE, or UNCLEAR."
                )
            else:
                if final_decision == "INCLUDE":
                    include_count += 1
                elif final_decision == "EXCLUDE":
                    exclude_count += 1
                else:
                    unclear_count += 1
                if isinstance(criteria, list) and criteria:
                    try:
                        expected = compute_final_decision(criteria)
                    except ValueError as exc:
                        errors.append(
                            f"Invalid criteria for study_index {study_index}: {exc}"
                        )
                    else:
                        if final_decision != expected:
                            errors.append(
                                f"final_decision {final_decision!r} for "
                                f"study_index {study_index} does not match "
                                f"get_final_decision rules (expected {expected!r})."
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
    if n_unclear is not None and n_unclear != unclear_count:
        errors.append(
            f"n_unclear is {n_unclear}, while the decisions list contains "
            f"{unclear_count} UNCLEAR decisions."
        )

    _raise_validation_errors(errors)
    return True
