"""
Report formatting tools for the Orchestrator agent.

Provides a deterministic ``format_report`` tool that takes structured
pipeline outputs and produces a consistent Markdown report — eliminating
the LLM's freedom to format differently on every run.

Also provides ``save_evidence_json`` to persist structured evidence data
as a separate JSON file alongside the report.
"""

import json
import re
from smolagents import tool


# ---------------------------------------------------------------------------
# Internal helpers (not exposed as tools)
# ---------------------------------------------------------------------------

# ---- Boilerplate handling ------------------------------------------------

_SECTION_HEADERS = [
    (1, re.compile(
        r"###\s*1\.\s*Task outcome\s*\(short version\)\s*:?\s*\n?", re.IGNORECASE
    )),
    (2, re.compile(
        r"###\s*2\.\s*Task outcome\s*\(extremely detailed version\)\s*:?\s*\n?",
        re.IGNORECASE,
    )),
    (3, re.compile(
        r"###\s*3\.\s*Additional context\s*\(if relevant\)\s*:?\s*\n?", re.IGNORECASE
    )),
]


# ---- Key alias registry ---------------------------------------------------
#
# Alias table: tolerates minor case or naming variations in agent
# output keys.  All lookups go through _alias_get(), which performs
# exact case-insensitive matching against the aliases listed here.

_KEY_ALIASES: dict[str, list[str]] = {
    # ---- Study-level fields ----
    "study_index":     ["study_index", "index", "study_id", "study_number"],
    "citation":        ["citation", "reference", "source", "ref"],
    "population":      ["population", "participants", "sample", "subjects",
                        "patients"],
    "setting":         ["setting", "location", "site", "context", "country"],
    "intervention":    ["intervention", "treatment", "exposure",
                        "experimental"],
    "comparator":      ["comparison", "comparator", "control",
                        "control_group", "placebo"],
    "outcomes":        ["outcomes", "outcome_data", "endpoints", "measures"],
    "study_design":    ["study_design", "design", "study_type", "methodology"],
    "follow_up":       ["follow_up", "followup", "follow_up_period",
                        "follow_up_duration", "duration"],
    "adverse_events":  ["adverse_events", "adverse", "side_effects", "harms",
                        "safety"],
    "key_findings":    ["key_findings", "findings", "main_findings",
                        "main_results"],
    "notes":           ["notes", "comments", "remarks", "additional_notes"],

    # ---- Outcome-level fields ----
    "outcome_name":    ["outcome_name", "name", "outcome", "endpoint",
                        "measure_name"],
    "effect_measure":  ["effect_measure", "measure", "statistic", "metric",
                        "effect_type"],
    "effect_size":     ["effect_size", "effect", "estimate", "point_estimate",
                        "value"],
    "ci":              ["ci_95", "ci", "confidence_interval", "conf_interval"],
    "ci_lower":        ["ci_95_lower", "ci_lower", "lower_ci", "lower_bound",
                        "ci_low"],
    "ci_upper":        ["ci_95_upper", "ci_upper", "upper_ci", "upper_bound",
                        "ci_high"],
    "p_value":         ["p_value", "p", "pvalue", "significance", "p_val"],

    # ---- Adverse-event sub-fields ----
    "event":           ["event", "adverse_event", "ae_name", "ae", "outcome"],
    "intervention_n":  ["intervention_n", "intervention_count", "treatment_n",
                        "experimental_n"],
    "control_n":       ["control_n", "control_count", "comparator_n",
                        "placebo_n"],

    # ---- Screening-decision fields ----
    "decision":        ["decision", "screening_decision", "verdict", "status"],
    "reason":          ["reason", "rationale", "justification", "explanation"],
    "decisions_list":  ["decisions", "screening_decisions",
                        "screening_results"],

    # ---- Critic / synthesis fields ----
    "synthesis":       ["synthesis", "narrative_synthesis", "narrative",
                        "summary", "conclusion"],
    "quality_assessment": ["quality_assessment", "quality_assessments",
                           "quality", "assessment"],
    "quality_rating":  ["quality_rating", "rating", "quality_score", "score",
                        "quality_grade"],
    "evidence_strength": ["evidence_strength", "strength", "certainty",
                          "grade", "confidence"],
    "limitations":     ["limitations", "weaknesses", "concerns"],
    "strengths":       ["strengths", "pros", "positive_aspects",
                        "strong_points"],
    "risk_of_bias":    ["risk_of_bias_concerns", "risk_of_bias",
                        "bias_concerns", "bias"],
    "applicability":   ["applicability", "generalizability",
                        "external_validity"],

    # ---- Container / wrapper fields ----
    "studies":         ["studies", "evidence", "extractions",
                        "extracted_studies", "included_studies"],
    "primary_findings": ["primary_findings", "main_findings", "key_results"],
    "extraction_notes": ["extraction_notes", "extraction_comments"],
    "results_summary": ["results_summary", "summary", "result", "definition"],
}


def _alias_get(d: dict, concept: str, *, default=None):
    """Look up a value in *d* using the alias list registered for *concept*.

    Aliases are tried in priority order with exact case-insensitive
    matching.  Returns the value even if it is ``""`` or ``[]``; only
    ``None`` is skipped so that the next alias can be tried.

    If *concept* is not in ``_KEY_ALIASES``, falls back to ``[concept]``.
    """
    if not isinstance(d, dict):
        return default
    aliases = _KEY_ALIASES.get(concept, [concept])
    d_lower: dict[str, str] = {k.lower(): k for k in d}

    for alias in aliases:
        orig_key = d_lower.get(alias.lower())
        if orig_key is not None:
            val = d[orig_key]
            if val is not None:
                return val

    return default


# ---- Study list extraction ------------------------------------------------

def _find_studies_list(data) -> list[dict]:
    """Extract the list of study dicts from miner output.

    Expects ``{"studies": [...]}`` (the prescribed schema) or a plain
    list.  Returns ``[]`` on failure.
    """
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    val = _alias_get(data, "studies")
    if isinstance(val, list):
        return val

    return []


# ---- Synthesis scaffold stripping ----------------------------------------

def _strip_synthesis_scaffold(text: str) -> str:
    """Remove raw tool-prompt scaffold text from critic synthesis output.

    Truncates at markers like ``=== EVIDENCE SYNTHESIS TASK ===``.
    """
    # Cut at "Automated synthesis summary (tool output):" or similar
    for marker in (
        "Automated synthesis summary (tool output)",
        "=== EVIDENCE SYNTHESIS TASK ===",
        "=== QUALITY ASSESSMENT TASK ===",
    ):
        idx = text.find(marker)
        if idx > 0:
            text = text[:idx].rstrip()
    return text


# ---- Boilerplate header stripping ----------------------------------------

_BOILERPLATE_HEADER_RE = re.compile(
    r"###\s*\d+\.\s*Task outcome\s*\([^)]*\)\s*:?\s*"
    r"|###\s*\d+\.\s*Additional context\s*\([^)]*\)\s*:?\s*",
    re.IGNORECASE,
)


def _strip_boilerplate_headers(text: str) -> str:
    """Remove ``### 1. Task outcome …`` / ``### 3. Additional context …``
    section headers that managed agents embed inside JSON field values.
    Keeps the body text beneath each header.
    """
    return _BOILERPLATE_HEADER_RE.sub("", text).strip()


def _get_boilerplate_sections(text: str) -> dict[int, str]:
    """Split a smolagents managed-agent response into its numbered sections.

    Returns a dict mapping section number (1, 2, 3) to the text content
    of that section (without the header line).  If the input does not
    contain boilerplate, returns ``{0: text}`` with the full input.

    If the text (after prefix stripping) is already valid JSON, it is
    returned unsplit as ``{0: text}`` to prevent regex patterns from
    matching inside JSON string keys.
    """
    # Strip the leading "Here is the final answer …" line
    text = re.sub(
        r"Here is the final answer from your managed agent.*?\n", "", text
    )

    # If the remaining text is valid JSON, do NOT split it —
    # the section-header patterns would match inside JSON keys like
    # '"### 1. Task outcome (short version)"' and produce garbage.
    stripped = text.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            json.loads(stripped)
            return {0: stripped}
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    # Locate each section header
    spans: list[tuple[int, int, int]] = []  # (section_num, start, end_of_header)
    for num, pat in _SECTION_HEADERS:
        m = pat.search(text)
        if m:
            spans.append((num, m.start(), m.end()))

    if not spans:
        return {0: text.strip()}

    spans.sort(key=lambda s: s[1])
    sections: dict[int, str] = {}
    for i, (num, _start, header_end) in enumerate(spans):
        if i + 1 < len(spans):
            body = text[header_end:spans[i + 1][1]]
        else:
            body = text[header_end:]
        sections[num] = body.strip()

    return sections


def _extract_json_from_text(text: str):
    """Try to extract and parse a JSON object or array from *text*.

    First tries to parse the whole string, then searches for the
    outermost ``{…}`` or ``[…]`` block.  Returns the parsed Python
    object on success, ``None`` on failure.
    """
    text = text.strip()
    # Whole-string parse
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    # Find outermost braces / brackets using a simple depth counter
    for open_ch, close_ch in [('{', '}'), ('[', ']')]:
        start_idx = text.find(open_ch)
        if start_idx == -1:
            continue
        depth = 0
        in_str = False
        escape = False
        for i in range(start_idx, len(text)):
            ch = text[i]
            if escape:
                escape = False
                continue
            if ch == '\\' and in_str:
                escape = True
                continue
            if ch == '"' and not escape:
                in_str = not in_str
                continue
            if in_str:
                continue
            if ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    candidate = text[start_idx:i + 1]
                    try:
                        return json.loads(candidate)
                    except (json.JSONDecodeError, TypeError, ValueError):
                        break  # try the other bracket type
    return None


def _extract_all_json_from_text(text: str) -> list:
    """Extract ALL top-level JSON objects and arrays from *text*.

    Returns a (possibly empty) list of parsed Python objects, in the
    order they appear in the text.
    """
    text = text.strip()
    results: list = []

    for open_ch, close_ch in [('{', '}'), ('[', ']')]:
        search_start = 0
        while search_start < len(text):
            start_idx = text.find(open_ch, search_start)
            if start_idx == -1:
                break
            depth = 0
            in_str = False
            escape = False
            found_end = -1
            for i in range(start_idx, len(text)):
                ch = text[i]
                if escape:
                    escape = False
                    continue
                if ch == '\\' and in_str:
                    escape = True
                    continue
                if ch == '"' and not escape:
                    in_str = not in_str
                    continue
                if in_str:
                    continue
                if ch == open_ch:
                    depth += 1
                elif ch == close_ch:
                    depth -= 1
                    if depth == 0:
                        found_end = i
                        break
            if found_end == -1:
                break
            candidate = text[start_idx:found_end + 1]
            try:
                results.append(json.loads(candidate))
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
            search_start = found_end + 1

    return results


def _find_json_with_keys(text: str, keys: list[str]):
    """Find the first JSON object in *text* that contains at least one of
    the specified *keys*.  Returns ``None`` if no matching dict is found,
    allowing the caller to fall through to alternative extraction."""
    all_objs = _extract_all_json_from_text(text)
    if not all_objs:
        return None
    # Return the first dict that has at least one of the expected keys
    for obj in all_objs:
        if isinstance(obj, dict) and any(k in obj for k in keys):
            return obj
    # If none matched, return the first dict (if any) as a loose fallback.
    # Do NOT return non-dict objects like [1] — they are accidental
    # fragments and would short-circuit the full-response parse.
    for obj in all_objs:
        if isinstance(obj, dict):
            return obj
    return None


def _extract_json_from_boilerplate(response: str, expected_keys: list[str] | None = None):
    """Extract the JSON payload from a smolagents boilerplate response.

    The structured JSON is always in section 2 ("extremely detailed version").
    When *expected_keys* is provided and section 2 contains multiple JSON
    objects, returns the first one that has at least one of those keys.
    Returns the parsed Python object, or ``None`` if extraction fails.
    """
    sections = _get_boilerplate_sections(response)
    # Section 2 normally holds the JSON
    if 2 in sections:
        if expected_keys:
            result = _find_json_with_keys(sections[2], expected_keys)
        else:
            result = _extract_json_from_text(sections[2])
        if result is not None:
            return result
    # Fallback: try the entire response
    if expected_keys:
        return _find_json_with_keys(response, expected_keys)
    return _extract_json_from_text(response)


# ---- Screening decisions -------------------------------------------------

def _normalize_decision(d: dict) -> dict:
    """Normalize a single screening-decision dict to use consistent keys."""
    return {
        "study_index": _alias_get(d, "study_index", default=0),
        "decision": (_alias_get(d, "decision", default="") or "").upper(),
        "reason": _alias_get(d, "reason", default=""),
    }


def _extract_decisions_list(data) -> list[dict] | None:
    """Given parsed JSON *data*, return the decisions list or None."""
    if isinstance(data, dict):
        decisions = _alias_get(data, "decisions_list")
        if isinstance(decisions, list):
            return [_normalize_decision(d) for d in decisions]
    if isinstance(data, list):
        return [_normalize_decision(d) for d in data]
    return None


def _parse_decisions(gatekeeper_response: str) -> list[dict]:
    """Best-effort extraction of screening decisions from the gatekeeper's
    free-form response string.  Handles both JSON and prose formats."""
    # First strip boilerplate and try JSON from section 2
    data = _extract_json_from_boilerplate(gatekeeper_response)
    result = _extract_decisions_list(data)
    if result is not None:
        return result

    # Try plain JSON
    try:
        data = json.loads(gatekeeper_response)
        result = _extract_decisions_list(data)
        if result is not None:
            return result
    except (json.JSONDecodeError, TypeError):
        pass

    # Try to find a JSON object with a decisions key embedded in the response
    json_match = re.search(
        r'\{[^{}]*"(?:screening_)?decisions"\s*:\s*\[.*?\]\s*\}',
        gatekeeper_response,
        re.DOTALL,
    )
    if json_match:
        try:
            data = json.loads(json_match.group())
            result = _extract_decisions_list(data)
            if result is not None:
                return result
        except (json.JSONDecodeError, TypeError):
            pass

    # Fallback: regex parse individual decision entries
    # Use a two-pass approach: first find each JSON-like object, then
    # extract fields within each bounded block.
    decisions: list[dict] = []
    # Match each {...} block that contains a study_index
    block_pattern = re.compile(
        r'\{[^{}]*?"study_index"[^{}]*?\}', re.DOTALL | re.IGNORECASE
    )
    idx_pat = re.compile(r'"?study_index"?\s*[:=]\s*(\d+)')
    dec_pat = re.compile(r'"?decision"?\s*[:=]\s*["\']?(INCLUDE|EXCLUDE)["\']?',
                         re.IGNORECASE)
    reason_pat = re.compile(
        r'"?(?:reason|rationale)"?\s*[:=]\s*"([^"]+)"', re.IGNORECASE
    )
    for block in block_pattern.finditer(gatekeeper_response):
        text = block.group()
        m_idx = idx_pat.search(text)
        m_dec = dec_pat.search(text)
        if m_idx and m_dec:
            m_reason = reason_pat.search(text)
            decisions.append({
                "study_index": int(m_idx.group(1)),
                "decision": m_dec.group(1).upper(),
                "reason": m_reason.group(1).strip() if m_reason else "",
            })

    # Last resort: look for simple patterns like "Study N: INCLUDE/EXCLUDE"
    if not decisions:
        simple = re.compile(
            r'(?:Study|study)\s*(\d+)\s*[:–—-]\s*(INCLUDE|EXCLUDE)\s*(?:[-–—:]\s*(.+?))?(?:\n|$)',
            re.IGNORECASE,
        )
        for m in simple.finditer(gatekeeper_response):
            decisions.append({
                "study_index": int(m.group(1)),
                "decision": m.group(2).upper(),
                "reason": (m.group(3) or "").strip(),
            })

    return decisions


# ---- Narrative synthesis -------------------------------------------------

def _extract_narrative_synthesis(critic_response: str) -> str:
    """Extract the narrative synthesis text from the critic's response,
    stripping JSON wrappers and boilerplate."""
    _CRITIC_KEYS = ["synthesis", "narrative_synthesis", "quality_assessments",
                    "quality_assessment", "evidence_strength"]
    # Try extracting JSON from boilerplate section 2 (key-aware)
    data = _extract_json_from_boilerplate(critic_response, expected_keys=_CRITIC_KEYS)
    if isinstance(data, dict):
        synth = _alias_get(data, "synthesis", default="")
        if synth:
            return _strip_boilerplate_headers(_strip_synthesis_scaffold(synth))

    # Try plain JSON parse
    try:
        data = json.loads(critic_response)
        if isinstance(data, dict):
            synth = _alias_get(data, "synthesis", default="")
            if synth:
                return _strip_boilerplate_headers(_strip_synthesis_scaffold(synth))
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback: return section 1 (short prose) — never return raw JSON
    sections = _get_boilerplate_sections(critic_response)
    if 1 in sections:
        return sections[1]

    return critic_response.strip()


# ---- Quality assessment --------------------------------------------------

def _format_quality_data(data: dict) -> str:
    """Given a parsed JSON dict from the critic, format quality assessment
    fields as human-readable Markdown prose."""
    qa = _alias_get(data, "quality_assessment", default="")
    strength = _alias_get(data, "evidence_strength", default="")
    limitations = _alias_get(data, "limitations", default=[])

    parts: list[str] = []
    if qa:
        if isinstance(qa, list):
            for item in qa:
                idx = _alias_get(item, "study_index", default="?")
                rating = _alias_get(item, "quality_rating", default="N/A")
                parts.append(f"- **Study {idx}:** Quality rating — {rating}")
                for s in (_alias_get(item, "strengths", default=[]) or []):
                    parts.append(f"  - Strength: {s}")
                for lim in (_alias_get(item, "limitations", default=[]) or []):
                    parts.append(f"  - Limitation: {lim}")
                for c in (_alias_get(item, "risk_of_bias", default=[]) or []):
                    parts.append(f"  - Bias concern: {c}")
                appl = _alias_get(item, "applicability", default="")
                if appl:
                    parts.append(f"  - Applicability: {appl}")
        elif isinstance(qa, str):
            parts.append(qa)
    if strength:
        parts.append(f"\n**Overall evidence strength:** {strength}")
    if limitations:
        parts.append("\n**Key limitations:**")
        if isinstance(limitations, list):
            for lim in limitations:
                parts.append(f"- {lim}")
        else:
            parts.append(str(limitations))
    return "\n".join(parts)


def _extract_quality_assessment(critic_response: str) -> str:
    """Extract quality assessment from the critic response."""
    _CRITIC_KEYS = ["quality_assessments", "quality_assessment",
                    "evidence_strength", "limitations", "synthesis"]
    # Try extracting JSON from boilerplate section 2 (key-aware)
    data = _extract_json_from_boilerplate(critic_response, expected_keys=_CRITIC_KEYS)
    if isinstance(data, dict):
        formatted = _format_quality_data(data)
        if formatted.strip():
            return formatted

    # Try plain JSON parse
    try:
        data = json.loads(critic_response)
        if isinstance(data, dict):
            formatted = _format_quality_data(data)
            if formatted.strip():
                return formatted
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback: return section 1 (short prose) — never return raw JSON
    sections = _get_boilerplate_sections(critic_response)
    if 1 in sections:
        return sections[1]

    return critic_response.strip()


# ---- Evidence prose ------------------------------------------------------

def _format_studies_as_prose(studies: list[dict]) -> str:
    """Convert a list of study dicts into human-readable prose."""
    parts: list[str] = []
    for study in studies:
        if not isinstance(study, dict):
            continue
        idx = _alias_get(study, "study_index", default="?")
        citation = _alias_get(study, "citation", default="")
        header = f"**Study {idx}**"
        if citation:
            header += f" — {citation}"
        parts.append(header)

        # Population / Participants
        pop = _alias_get(study, "population", default="")
        if pop:
            if isinstance(pop, dict):
                pop = "; ".join(f"{k}: {v}" for k, v in pop.items())
            parts.append(f"- **Population:** {pop}")

        # Setting
        setting = _alias_get(study, "setting", default="")
        if setting:
            parts.append(f"- **Setting:** {setting}")

        # Intervention
        interv = _alias_get(study, "intervention", default="")
        if interv:
            if isinstance(interv, dict):
                interv = "; ".join(f"{k}: {v}" for k, v in interv.items())
            parts.append(f"- **Intervention:** {interv}")

        # Comparator
        comp = _alias_get(study, "comparator", default="")
        if comp:
            parts.append(f"- **Comparator:** {comp}")

        # Outcomes
        outcomes = _alias_get(study, "outcomes", default="")
        if outcomes:
            if isinstance(outcomes, list):
                parts.append("- **Outcomes:**")
                for o in outcomes:
                    if isinstance(o, dict):
                        name = _alias_get(o, "outcome_name", default="")
                        measure = _alias_get(o, "effect_measure", default="")
                        effect = _alias_get(o, "effect_size", default="")
                        # CI: prefer separate lower/upper bounds;
                        # fall back to a single CI string if neither exists.
                        ci_lo = _alias_get(o, "ci_lower", default="")
                        ci_hi = _alias_get(o, "ci_upper", default="")
                        if ci_lo and ci_hi:
                            ci = f"{ci_lo}\u2013{ci_hi}"
                        else:
                            ci = _alias_get(o, "ci", default="")
                        p = _alias_get(o, "p_value", default="")
                        # Build the effect portion, skipping None/empty values
                        effect_parts = []
                        if measure:
                            effect_parts.append(str(measure))
                        if effect is not None and effect != "":
                            effect_parts.append(str(effect))
                        effect_str = " ".join(effect_parts)
                        line = f"  - {name}"
                        if effect_str:
                            line += f": {effect_str}"
                        if ci:
                            line += f" (95% CI {ci})"
                        if p and p != "NA":
                            line += f"; p={p}"
                        parts.append(line)
                    elif isinstance(o, str):
                        parts.append(f"  - {o}")
            elif isinstance(outcomes, dict):
                parts.append("- **Outcomes:**")
                for k, v in outcomes.items():
                    if isinstance(v, dict):
                        summary = _alias_get(v, "results_summary",
                                             default=None) or str(v)
                        parts.append(f"  - {k}: {summary}")
                    else:
                        parts.append(f"  - {k}: {v}")
            else:
                parts.append(f"- **Outcomes:** {outcomes}")

        # Adverse events
        ae = _alias_get(study, "adverse_events", default="")
        if ae:
            if isinstance(ae, list):
                parts.append("- **Adverse events:**")
                for a in ae:
                    if isinstance(a, dict):
                        event = _alias_get(a, "event", default="")
                        i_n = _alias_get(a, "intervention_n", default="")
                        c_n = _alias_get(a, "control_n", default="")
                        p = _alias_get(a, "p_value", default="")
                        parts.append(
                            f"  - {event}: {i_n} vs {c_n}"
                            + (f" (p={p})" if p and p != "NA" else "")
                        )
                    else:
                        parts.append(f"  - {a}")
            elif isinstance(ae, dict):
                parts.append("- **Adverse events:**")
                for k, v in ae.items():
                    parts.append(f"  - {k}: {v}")
            elif isinstance(ae, str):
                parts.append(f"- **Adverse events:** {ae}")

        # Study design
        design = _alias_get(study, "study_design", default="")
        if design:
            if isinstance(design, dict):
                design = "; ".join(f"{k}: {v}" for k, v in design.items())
            parts.append(f"- **Study design:** {design}")

        # Follow-up
        fu = _alias_get(study, "follow_up", default="")
        if fu:
            parts.append(f"- **Follow-up:** {fu}")

        # Key findings (from primary_findings at top level or within study)
        kf = _alias_get(study, "key_findings", default=[]) or []
        if kf:
            parts.append("- **Key findings:**")
            for finding in kf:
                parts.append(f"  - {finding}")

        # Notes
        notes = _alias_get(study, "notes", default="")
        if notes:
            # Strip boilerplate headers that agents embed in notes
            if isinstance(notes, str):
                notes = _strip_boilerplate_headers(notes)
            if isinstance(notes, dict):
                parts.append("- **Notes:**")
                for nk, nv in notes.items():
                    if isinstance(nv, list):
                        parts.append(f"  - {nk}:")
                        for item in nv:
                            parts.append(f"    - {item}")
                    else:
                        parts.append(f"  - {nk}: {nv}")
            elif isinstance(notes, list):
                parts.append("- **Notes:**")
                for n in notes:
                    parts.append(f"  - {n}")
            else:
                parts.append(f"- **Notes:** {notes}")

        parts.append("")  # blank line between studies

    return "\n".join(parts)


def _extract_evidence_prose(miner_response: str) -> str:
    """Convert miner evidence JSON into human-readable prose for the report."""
    # Try extracting JSON from boilerplate section 2
    data = _extract_json_from_boilerplate(miner_response)

    if isinstance(data, dict):
        studies = _find_studies_list(data)
        if studies:
            prose_parts = [_format_studies_as_prose(studies)]
            # Include primary findings if present
            pf = _alias_get(data, "primary_findings", default=[]) or []
            if pf and isinstance(pf, list):
                prose_parts.append("\n**Primary findings:**")
                for finding in pf:
                    prose_parts.append(f"- {finding}")
            # Include extraction notes if present
            en = _alias_get(data, "extraction_notes", default=[]) or []
            if en and isinstance(en, list):
                prose_parts.append("\n**Extraction notes:**")
                for note in en:
                    prose_parts.append(f"- {note}")
            return "\n".join(prose_parts)

    if isinstance(data, list) and data:
        return _format_studies_as_prose(data)

    # Try plain JSON parse
    try:
        data = json.loads(miner_response)
        if isinstance(data, dict):
            studies = _find_studies_list(data)
            if studies:
                return _format_studies_as_prose(studies)
        elif isinstance(data, list):
            return _format_studies_as_prose(data)
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback: return ONLY section 1 (short prose) — never include raw JSON
    sections = _get_boilerplate_sections(miner_response)
    if 1 in sections:
        return sections[1]

    return miner_response.strip()


# ---------------------------------------------------------------------------
# Tools exposed to the Orchestrator agent
# ---------------------------------------------------------------------------

@tool
def extract_included_studies(
    screening_response: str,
    candidates_json: str,
) -> str:
    """
    Parse the gatekeeper's screening response and return the INCLUDED
    studies ready for the miner, as a JSON string.

    This tool robustly extracts screening decisions from the gatekeeper's
    response (handling boilerplate wrappers, JSON and prose formats),
    filters to INCLUDE decisions, matches them back to the candidate
    studies, and returns a JSON list of study objects with title, abstract,
    and study_index.

    Args:
        screening_response: The full string response from the gatekeeper agent.
        candidates_json: JSON string containing the candidate studies
            (as returned by get_candidates_json) with a 'studies' key.

    Returns:
        A JSON string: a list of included study objects (each with
        study_index, title, abstract).  Returns '[]' if no studies
        were included or parsing failed.
    """
    # Parse the screening decisions using the robust multi-fallback parser
    decisions = _parse_decisions(screening_response)
    included_indices = {
        d["study_index"] for d in decisions
        if d.get("decision", "").upper() == "INCLUDE"
    }

    # Parse the candidate studies
    try:
        review_data = json.loads(candidates_json)
    except (json.JSONDecodeError, TypeError):
        review_data = {}

    studies = review_data.get("studies", [])

    # Build the index-to-study mapping
    study_by_index: dict[int, dict] = {}
    for i, s in enumerate(studies):
        idx = s.get("study_index", i + 1)
        study_by_index[idx] = s

    # Collect included studies
    included: list[dict] = []
    for idx in sorted(included_indices):
        if idx in study_by_index:
            s = study_by_index[idx]
            included.append({
                "study_index": idx,
                "title": s.get("title", ""),
                "abstract": s.get("abstract", ""),
            })

    return json.dumps(included, ensure_ascii=False)


@tool
def format_report(
    review_title: str,
    review_objective: str,
    num_candidates: int,
    screening_response: str,
    evidence_response: str,
    synthesis_response: str,
) -> str:
    """
    Format a consistent Markdown systematic review report from pipeline outputs.

    Takes the raw string responses from each agent and produces a clean,
    human-readable Markdown report with NO raw JSON. Call this as the LAST
    step before returning the final answer.

    Args:
        review_title: Title of the systematic review.
        review_objective: Research objective of the review.
        num_candidates: Number of candidate studies found by the librarian.
        screening_response: The full string response from the gatekeeper agent.
        evidence_response: The full string response from the miner agent.
        synthesis_response: The full string response from the critic agent.

    Returns:
        A clean Markdown-formatted systematic review report.
    """
    # --- Parse screening decisions ---
    decisions = _parse_decisions(screening_response)
    included = [d for d in decisions if d.get("decision", "").upper() == "INCLUDE"]
    excluded = [d for d in decisions if d.get("decision", "").upper() == "EXCLUDE"]
    n_included = len(included)
    n_excluded = len(excluded)

    # If parsing failed, try counting from the text
    if not decisions:
        inc_matches = re.findall(r'INCLUDE', screening_response, re.IGNORECASE)
        exc_matches = re.findall(r'EXCLUDE', screening_response, re.IGNORECASE)
        n_included = len(inc_matches)
        n_excluded = len(exc_matches)

    # --- Build screening decisions text ---
    decisions_text_parts = []
    sorted_decisions = sorted(decisions, key=lambda d: d.get("study_index", 0))
    for d in sorted_decisions:
        idx = _alias_get(d, "study_index", default="?")
        dec = _alias_get(d, "decision", default="?")
        reason = _alias_get(d, "reason", default="")
        line = f"  - Study {idx}: {dec}"
        if reason:
            line += f" — {reason}"
        decisions_text_parts.append(line)
    decisions_text = "\n".join(decisions_text_parts)

    # --- Build evidence summary (prose, not JSON) ---
    evidence_prose = _extract_evidence_prose(evidence_response)

    # --- Build synthesis/conclusions ---
    synthesis_text = _extract_narrative_synthesis(synthesis_response)

    # --- Build quality assessment ---
    quality_text = _extract_quality_assessment(synthesis_response)

    # --- Assemble the final report ---
    report = f"""# Systematic Review Report

## 1. Review Summary
- **Title:** {review_title}
- **Objective:** {review_objective}

## 2. Search Results
- Number of candidate studies found: {num_candidates}

## 3. Screening Results
- Included studies: {n_included}
- Excluded studies: {n_excluded}
- Decisions:
{decisions_text}

## 4. Evidence Extraction Summary
{evidence_prose}

## 5. Synthesis & Conclusions
{synthesis_text}

## 6. Quality Assessment
{quality_text}
"""
    return report.strip()


@tool
def save_evidence_json(
    evidence_response: str,
    screening_response: str,
    synthesis_response: str,
    output_dir: str,
) -> str:
    """
    Save structured evidence, screening and quality data as a JSON file
    alongside the report.  This preserves the machine-readable data
    without polluting the human-readable Markdown report.

    Args:
        evidence_response: The raw string response from the miner agent.
        screening_response: The raw string response from the gatekeeper agent.
        synthesis_response: The raw string response from the critic agent.
        output_dir: Path to the run output directory where the JSON should be saved.

    Returns:
        The path to the saved JSON file, or a message if saving failed.
    """
    import os

    result: dict = {
        "screening_decisions": [],
        "evidence": [],
        "quality_assessment": [],
        "synthesis": "",
    }

    # ---- Screening decisions ----
    result["screening_decisions"] = _parse_decisions(screening_response)

    # ---- Evidence (from miner) ----
    data = _extract_json_from_boilerplate(evidence_response)
    if isinstance(data, dict):
        result["evidence"] = _find_studies_list(data) or [data]
        # Preserve extra top-level fields
        for key in ("primary_findings", "extraction_notes"):
            val = _alias_get(data, key)
            if val is not None:
                result[key] = val
    elif isinstance(data, list):
        result["evidence"] = data
    else:
        # Absolute fallback — try plain JSON
        try:
            parsed = json.loads(evidence_response)
            if isinstance(parsed, dict):
                result["evidence"] = _find_studies_list(parsed) or [parsed]
            elif isinstance(parsed, list):
                result["evidence"] = parsed
        except (json.JSONDecodeError, TypeError):
            result["evidence_raw"] = evidence_response

    # ---- Quality / synthesis (from critic) ----
    _CRITIC_KEYS = ["quality_assessments", "quality_assessment",
                    "evidence_strength", "limitations", "synthesis",
                    "narrative_synthesis"]
    critic_data = _extract_json_from_boilerplate(synthesis_response, expected_keys=_CRITIC_KEYS)
    if isinstance(critic_data, dict):
        result["quality_assessment"] = _alias_get(
            critic_data, "quality_assessment", default=[]
        )
        result["synthesis"] = _alias_get(
            critic_data, "synthesis", default=""
        )
        es = _alias_get(critic_data, "evidence_strength")
        if es is not None:
            result["evidence_strength"] = es
        lims = _alias_get(critic_data, "limitations")
        if lims is not None:
            result["limitations"] = lims

    output_path = os.path.join(output_dir, "evidence.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return f"Evidence saved to {output_path}"
    except Exception as e:
        return f"Failed to save evidence JSON: {e}"
