#!/usr/bin/env python3
"""Render Bastirr workflow logs as presentation-friendly HTML.

This is a standalone exporter for presentation/demo use. It reads a
``workflow.log`` file, optionally enriches it with a sibling
``activity.md`` file, and writes a single self-contained HTML document
with collapsible sections and code toggles.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer


ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
STEP_LINE_RE = re.compile(r"^━+\s*Step\s+(\d+)\s*━+$")
PLAN_LINE_RE = re.compile(r"^─+\s*(Initial plan|Updated plan)\s*─+$")
PANEL_START_RE = re.compile(r"^╭.*New run(?: - ([^ ]+))?.*╮$")
PANEL_END_RE = re.compile(r"^╰.*╯$")
STATS_LINE_RE = re.compile(
    r"^\[Step\s+\d+:\s+Duration\s+.+?\|\s+Input tokens:\s+.+?\|\s+Output tokens:\s+.+?\]$"
)
MD_PHASE_RE = re.compile(r"^###\s+(\d+)\.\s+(.+)$")
MD_META_RE = re.compile(r"^\*(.+)\*$")
META_LINE_RE = re.compile(r"^> \*\*(.+?):\*\* (.*?)(?:\s{2})?$")
URL_RE = re.compile(r"https?://[^\s<]+")
RUN_ID_RE = re.compile(r"^(\d{8}_\d{6})")
STEP_MARKER_RE = re.compile(r"\bStep\s+(\d+)\b")


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_LEXER = PythonLexer(stripnl=False)
PYGMENTS_FORMATTER = HtmlFormatter(nowrap=True, style="native", classprefix="tok-")
PYGMENTS_CSS = PYGMENTS_FORMATTER.get_style_defs(".code-content")


@dataclass
class Block:
    kind: str
    content: str
    title: str = ""


@dataclass
class Section:
    kind: str
    raw_title: str
    raw_lines: list[str]
    blocks: list[Block] = field(default_factory=list)
    section_id: str = ""
    display_title: str = ""
    subtitle: str = ""
    phase_meta: str = ""
    phase_summary: str = ""
    annotation: dict | None = None


@dataclass
class ActivityPhase:
    number: int
    title: str
    meta: str
    summary: str


@dataclass
class ActivityData:
    metadata: dict[str, str] = field(default_factory=dict)
    resource_headers: list[str] = field(default_factory=list)
    resource_rows: list[list[str]] = field(default_factory=list)
    phases: list[ActivityPhase] = field(default_factory=list)


@dataclass
class AnnotationData:
    hero: dict | None = None
    sections: dict[str, dict] = field(default_factory=dict)


@dataclass
class ReviewProtocol:
    title: str = ""
    objective: str = ""
    background: str = ""
    selection_criteria: str = ""


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a Bastirr workflow.log into presentation-friendly HTML."
    )
    parser.add_argument("--workflow", required=True, help="Path to workflow.log")
    parser.add_argument(
        "--activity",
        default=None,
        help="Optional path to activity.md (defaults to sibling file if present)",
    )
    parser.add_argument(
        "--annotations",
        default=None,
        help="Optional path to annotations JSON",
    )
    parser.add_argument(
        "--disable-annotations",
        action="store_true",
        help="Disable annotations entirely, even if an annotations file is provided",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output HTML path (defaults to workflow_presentation.html alongside workflow.log)",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional HTML page title override",
    )
    parser.add_argument(
        "--hide-code-default",
        default="true",
        choices=["true", "false"],
        help="Hide raw <code> blocks by default",
    )
    parser.add_argument(
        "--hide-executed-code-default",
        default="true",
        choices=["true", "false"],
        help="Hide 'Executing parsed code' blocks by default",
    )
    return parser.parse_args()


def parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text).replace("\r\n", "\n")


def normalize_title(path: Path, override: str | None) -> str:
    if override:
        return override
    match = RUN_ID_RE.match(path.parent.name)
    if match:
        return f"Agent Run — SR{match.group(1)}"
    return f"Agent Run — {path.parent.name}"


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT.parent))
    except ValueError:
        try:
            return f"{REPO_ROOT.name}/{resolved.relative_to(REPO_ROOT)}"
        except ValueError:
            return str(resolved)


def parse_annotations(path: Path | None) -> AnnotationData:
    if path is None or not path.exists():
        return AnnotationData()

    try:
        data = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError):
        return AnnotationData()

    hero = data.get("hero")
    sections = data.get("sections", {})
    if not isinstance(sections, dict):
        sections = {}
    return AnnotationData(hero=hero if isinstance(hero, dict) else None, sections=sections)


def is_nested_run_start(line: str) -> bool:
    return bool(PANEL_START_RE.match(line) and " - " in line)


def parse_workflow_sections(text: str) -> list[Section]:
    lines = strip_ansi(text).splitlines()
    sections: list[Section] = []

    current_kind = "intro"
    current_title = "Intro"
    current_lines: list[str] = []
    nested_active = False
    nested_completed = False

    def flush() -> None:
        nonlocal current_lines, current_title, current_kind
        if not current_lines:
            return
        sections.append(Section(kind=current_kind, raw_title=current_title, raw_lines=current_lines[:]))
        current_lines = []

    for line in lines:
        if nested_active and nested_completed and line.startswith("Execution logs:"):
            nested_active = False
            nested_completed = False

        if not nested_active:
            plan_match = PLAN_LINE_RE.match(line)
            step_match = STEP_LINE_RE.match(line)

            if plan_match:
                flush()
                current_kind = "planning"
                current_title = plan_match.group(1).title()
                current_lines = [line]
                continue

            if step_match:
                flush()
                current_kind = "step"
                current_title = f"Step {step_match.group(1)}"
                current_lines = [line]
                continue

        current_lines.append(line)

        if is_nested_run_start(line):
            nested_active = True
            nested_completed = False
        elif nested_active and line.startswith("Final answer:"):
            nested_completed = True

    flush()

    for section in sections:
        section.blocks = parse_section_blocks(section)

    return sections


def parse_section_blocks(section: Section) -> list[Block]:
    lines = section.raw_lines[:]
    if section.kind in {"planning", "step"} and lines:
        lines = lines[1:]

    if section.kind == "planning":
        content_lines = [line for line in lines if line.strip() != "```"]
        content = "\n".join(content_lines).strip()
        return [Block(kind="planning", title=section.raw_title, content=content)] if content else []

    blocks: list[Block] = []
    i = 0
    while i < len(lines):
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        if PANEL_START_RE.match(line):
            panel_lines = [line]
            i += 1
            while i < len(lines):
                panel_lines.append(lines[i])
                if PANEL_END_RE.match(lines[i]):
                    i += 1
                    break
                i += 1
            title = panel_block_title(panel_lines[0])
            blocks.append(Block(kind="run_panel", title=title, content=clean_panel_text(panel_lines)))
            continue

        if line.startswith("Output message of the LLM:"):
            i += 1
            thought_lines: list[str] = []
            while i < len(lines) and not is_block_boundary(lines[i]):
                thought_lines.append(lines[i])
                i += 1
            content = "\n".join(thought_lines).strip()
            if content.startswith("Thought:"):
                content = content[len("Thought:"):].lstrip()
            if content:
                blocks.append(Block(kind="thought", title="Thought", content=content))
            continue

        if line.startswith("<code>"):
            i += 1
            code_lines: list[str] = []
            while i < len(lines) and not is_code_stop(lines[i]):
                code_lines.append(lines[i])
                i += 1
            content = "\n".join(code_lines).rstrip()
            if content:
                blocks.append(Block(kind="code", title="Code", content=content))
            continue

        if line.startswith(" ─ Executing parsed code:"):
            i += 1
            exec_lines: list[str] = []
            while i < len(lines) and not is_executed_stop(lines[i]):
                exec_lines.append(lines[i])
                i += 1
            content = "\n".join(exec_lines).rstrip()
            if content:
                blocks.append(Block(kind="executed_code", title="Executed Code", content=content))
            continue

        if line.startswith("Final answer:"):
            final_lines = [line[len("Final answer:"):].lstrip()]
            i += 1
            while i < len(lines) and not is_final_answer_stop(lines[i]):
                final_lines.append(lines[i])
                i += 1
            content = "\n".join(final_lines).strip()
            if content:
                blocks.append(Block(kind="final_answer", title="Final Answer", content=content))
            continue

        if line.startswith("Execution logs:"):
            log_lines = [line]
            i += 1
            while i < len(lines) and not is_block_boundary(lines[i]) and not STATS_LINE_RE.match(lines[i]):
                log_lines.append(lines[i])
                i += 1
            blocks.append(Block(kind="execution_logs", title="Execution Logs", content="\n".join(log_lines).strip()))
            continue

        if STATS_LINE_RE.match(line):
            blocks.append(Block(kind="stats", title="Step Stats", content=line.strip()))
            i += 1
            continue

        if line.startswith("Out:"):
            blocks.append(Block(kind="stats", title="Output", content=line.strip()))
            i += 1
            continue

        raw_lines = [line]
        i += 1
        while i < len(lines) and not is_block_boundary(lines[i]) and not STATS_LINE_RE.match(lines[i]) and not lines[i].startswith("Out:"):
            raw_lines.append(lines[i])
            i += 1
        content = "\n".join(raw_lines).strip()
        if content:
            blocks.append(Block(kind="raw_output", title="Workflow Output", content=content))

    return blocks


def is_block_boundary(line: str) -> bool:
    return (
        bool(PANEL_START_RE.match(line))
        or line.startswith("Output message of the LLM:")
        or line.startswith("<code>")
        or line.startswith(" ─ Executing parsed code:")
        or line.startswith("Final answer:")
        or line.startswith("Execution logs:")
    )


def is_code_stop(line: str) -> bool:
    return (
        line.startswith(" ─ Executing parsed code:")
        or line.startswith("Final answer:")
        or bool(PANEL_START_RE.match(line))
        or line.startswith("Execution logs:")
    )


def is_executed_stop(line: str) -> bool:
    return (
        line.startswith("Execution logs:")
        or line.startswith("Final answer:")
        or bool(PANEL_START_RE.match(line))
        or line.startswith("Output message of the LLM:")
        or STATS_LINE_RE.match(line) is not None
    )


def is_final_answer_stop(line: str) -> bool:
    return (
        bool(PANEL_START_RE.match(line))
        or line.startswith("Output message of the LLM:")
        or line.startswith("Execution logs:")
        or STATS_LINE_RE.match(line) is not None
        or line.startswith("Out:")
    )


def panel_block_title(start_line: str) -> str:
    match = PANEL_START_RE.match(start_line)
    if not match:
        return "Run Panel"
    agent = match.group(1)
    if agent:
        return f"Agent Input — {agent.title()}"
    return "Task Input"


def clean_panel_text(lines: Iterable[str]) -> str:
    cleaned: list[str] = []
    for line in lines:
        if line.startswith("│"):
            body = line[1:]
            if body.endswith("│"):
                body = body[:-1]
            if body.startswith(" "):
                body = body[1:]
            if body.endswith(" "):
                body = body[:-1]
            cleaned.append(body.rstrip())
    return "\n".join(cleaned).strip()


def parse_activity_md(path: Path | None) -> ActivityData | None:
    if path is None or not path.exists():
        return None

    lines = strip_ansi(read_text(path)).splitlines()
    data = ActivityData()
    i = 0

    while i < len(lines):
        line = lines[i]

        meta_match = META_LINE_RE.match(line)
        if meta_match:
            key = meta_match.group(1).strip()
            value = meta_match.group(2).strip()
            data.metadata[key] = value
            i += 1
            continue

        if line.startswith("| Agent |"):
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            headers, rows = parse_markdown_table(table_lines)
            data.resource_headers = headers
            data.resource_rows = rows
            continue

        phase_match = MD_PHASE_RE.match(line)
        if phase_match:
            number = int(phase_match.group(1))
            title = phase_match.group(2).strip()
            i += 1
            meta = ""
            summary_lines: list[str] = []
            seen_summary = False

            while i < len(lines) and not MD_PHASE_RE.match(lines[i]):
                if lines[i].strip() == "---":
                    i += 1
                    break
                meta_match = MD_META_RE.match(lines[i].strip())
                if meta_match and not meta:
                    meta = meta_match.group(1).strip()
                    i += 1
                    continue
                if lines[i].startswith("> "):
                    i += 1
                    continue
                if lines[i].strip():
                    summary_lines.append(lines[i].strip())
                    seen_summary = True
                elif seen_summary:
                    # Only keep the first narrative paragraph
                    pass
                i += 1

            summary = " ".join(summary_lines).strip()
            data.phases.append(ActivityPhase(number=number, title=title, meta=meta, summary=summary))
            continue

        i += 1

    return data


def parse_review_protocol(text: str) -> ReviewProtocol | None:
    cleaned = strip_ansi(text)
    lines = cleaned.splitlines()
    start_index = None

    for index, raw_line in enumerate(lines):
        if raw_line.strip() == "=== REVIEW PROTOCOL ===":
            start_index = index + 1
            break

    if start_index is None:
        return None

    key_map = {
        "title": "title",
        "objective": "objective",
        "background": "background",
        "selection criteria": "selection_criteria",
    }
    protocol = ReviewProtocol()
    current_key: str | None = None

    for raw_line in lines[start_index:]:
        line = raw_line.strip()
        if line in {"=== REVIEW PROTOCOL END ===", "Out: None"}:
            break
        if STATS_LINE_RE.match(line):
            break
        if not line or line == "=== REVIEW PROTOCOL ===":
            continue

        heading_match = re.match(
            r"^(Title|Objective|Background|Selection Criteria)\s*:\s*(.*)$",
            line,
            re.I,
        )
        if heading_match:
            heading = heading_match.group(1).strip().lower()
            current_key = key_map.get(heading)
            if current_key:
                existing = getattr(protocol, current_key)
                value = heading_match.group(2).strip()
                setattr(protocol, current_key, f"{existing} {value}".strip() if existing else value)
            continue

        if current_key:
            existing = getattr(protocol, current_key)
            setattr(protocol, current_key, f"{existing} {line}".strip())

    for field_name in ("title", "objective", "background", "selection_criteria"):
        value = getattr(protocol, field_name)
        setattr(protocol, field_name, re.sub(r"\s+", " ", value).strip())

    if not any(
        [
            protocol.title,
            protocol.objective,
            protocol.background,
            protocol.selection_criteria,
        ]
    ):
        return None

    return protocol


def parse_markdown_table(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    headers: list[str] = []
    rows: list[list[str]] = []
    for idx, line in enumerate(lines):
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if idx == 0:
            headers = parts
        elif idx == 1:
            continue
        else:
            rows.append(parts)
    return headers, rows


def enrich_sections(sections: list[Section], activity: ActivityData | None, annotations: AnnotationData) -> None:
    non_intro = [section for section in sections if section.kind != "intro"]

    if activity and activity.phases:
        for index, section in enumerate(non_intro, start=1):
            if index <= len(activity.phases):
                phase = activity.phases[index - 1]
                section.section_id = f"phase-{index}"
                section.display_title = phase.title
                section.subtitle = section.raw_title
                section.phase_meta = phase.meta
                section.phase_summary = phase.summary
            else:
                section.section_id = f"section-{index}"
                section.display_title = section.raw_title
    else:
        for index, section in enumerate(non_intro, start=1):
            section.section_id = f"section-{index}"
            section.display_title = section.raw_title

    for section in non_intro:
        if section.section_id in annotations.sections:
            section.annotation = annotations.sections[section.section_id]
        else:
            section.annotation = None

    intro = next((section for section in sections if section.kind == "intro"), None)
    if intro:
        intro.display_title = "Intro"
        intro.annotation = None


def parse_header_metadata(intro: Section) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in intro.raw_lines:
        if ":" not in line:
            continue
        if line.startswith("Review:"):
            metadata["Review"] = line.split(":", 1)[1].strip()
        elif line.startswith("Run directory:"):
            metadata["Run directory"] = line.split(":", 1)[1].strip()
        elif line.startswith("Started:"):
            metadata["Started"] = line.split(":", 1)[1].strip()
    return metadata


def format_json_if_possible(text: str) -> str:
    stripped = text.strip()
    if not stripped or stripped[0] not in "{[" or stripped[-1] not in "}]":
        return text

    candidates = [stripped]
    collapsed = re.sub(r"\s*\n\s*", " ", stripped)
    if collapsed != stripped:
        candidates.append(collapsed)

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        return json.dumps(parsed, indent=2, ensure_ascii=False)

    return text


def render_inline_html(text: object) -> str:
    value = str(text)
    parts: list[str] = []
    last_index = 0

    for match in URL_RE.finditer(value):
        if match.start() > last_index:
            parts.append(render_simple_markdown(value[last_index:match.start()]))
        url = match.group(0)
        safe_url = escape(url)
        parts.append(
            f'<a href="{safe_url}" target="_blank" rel="noreferrer">{safe_url}</a>'
        )
        last_index = match.end()

    if last_index < len(value):
        parts.append(render_simple_markdown(value[last_index:]))

    return "".join(parts) if parts else render_simple_markdown(value)


def render_simple_markdown(text: str) -> str:
    escaped = escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)


def scan_python_quote_state(line: str) -> tuple[str | None, str | None]:
    in_single: str | None = None
    in_triple: str | None = None
    escaped = False
    i = 0

    while i < len(line):
        ch = line[i]

        if in_triple:
            if line.startswith(in_triple, i):
                in_triple = None
                i += 3
                continue
            i += 1
            continue

        if in_single:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == in_single:
                in_single = None
            i += 1
            continue

        if ch == "#":
            break
        if line.startswith('"""', i) or line.startswith("'''", i):
            in_triple = line[i : i + 3]
            i += 3
            continue
        if ch in {"'", '"'}:
            in_single = ch
        i += 1

    return in_single, in_triple


def scan_python_bracket_depth(line: str) -> int:
    depth = 0
    in_single: str | None = None
    in_triple: str | None = None
    escaped = False
    i = 0

    while i < len(line):
        ch = line[i]

        if in_triple:
            if line.startswith(in_triple, i):
                in_triple = None
                i += 3
                continue
            i += 1
            continue

        if in_single:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == in_single:
                in_single = None
            i += 1
            continue

        if ch == "#":
            break
        if line.startswith('"""', i) or line.startswith("'''", i):
            in_triple = line[i : i + 3]
            i += 3
            continue
        if ch in {"'", '"'}:
            in_single = ch
            i += 1
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        i += 1

    return depth


def indentation_width(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def should_join_wrapped_collection_line(current: str, continuation: str) -> bool:
    if not current or not continuation.strip():
        return False
    if indentation_width(continuation) >= indentation_width(current):
        return False
    if scan_python_bracket_depth(current) <= 0:
        return False

    stripped = continuation.lstrip()
    if stripped.startswith(("#", ")", "]", "}")):
        return False

    starts_like_continuation = bool(
        re.match(r'^(?:[rubfRUBF]*["\']|[A-Za-z0-9_([{])', stripped)
    )
    return starts_like_continuation and current.rstrip().endswith(",")


def normalize_python_code(code: str) -> str:
    if not code:
        return ""

    source_lines = [line.rstrip() for line in code.splitlines()]
    string_normalized: list[str] = []
    index = 0

    while index < len(source_lines):
        current = source_lines[index]
        index += 1

        if not current:
            string_normalized.append(current)
            continue

        in_single, in_triple = scan_python_quote_state(current)
        while in_single and not in_triple and index < len(source_lines):
            continuation = source_lines[index]
            if not continuation:
                break
            current = f"{current.rstrip()} {continuation.lstrip()}"
            index += 1
            in_single, in_triple = scan_python_quote_state(current)

        string_normalized.append(current)

    normalized: list[str] = []
    index = 0

    while index < len(string_normalized):
        current = string_normalized[index]
        index += 1

        while index < len(string_normalized):
            continuation = string_normalized[index]
            if not should_join_wrapped_collection_line(current, continuation):
                break
            current = f"{current.rstrip()} {continuation.lstrip()}"
            index += 1

        normalized.append(current)

    return "\n".join(normalized)


def highlight_python(code: str) -> str:
    if not code:
        return ""
    try:
        return highlight(normalize_python_code(code), PYTHON_LEXER, PYGMENTS_FORMATTER)
    except Exception:
        return escape(code)


def render_html(
    *,
    page_title: str,
    workflow_path: Path,
    activity_path: Path | None,
    sections: list[Section],
    activity: ActivityData | None,
    annotations: AnnotationData,
    protocol: ReviewProtocol | None,
    hide_code_default: bool,
    hide_executed_default: bool,
) -> str:
    intro = next(section for section in sections if section.kind == "intro")
    other_sections = [section for section in sections if section.kind != "intro"]
    header_metadata = parse_header_metadata(intro)
    has_annotations = bool(annotations.hero or any(section.annotation for section in other_sections))

    summary_items = activity.metadata if activity else header_metadata
    intro_blocks_html = "\n".join(render_block(block) for block in intro.blocks)
    hero_html = render_annotation(annotations.hero, extra_class="hero-callout") if annotations.hero else ""
    resource_table_html = render_resource_table(activity) if activity and activity.resource_rows else ""
    protocol_html = render_protocol_section(protocol) if protocol else ""
    section_cards = "\n".join(render_section(section) for section in other_sections)

    body_classes = []
    body_classes.append("hide-annotations")
    if hide_code_default:
        body_classes.append("hide-code")
    if hide_executed_default:
        body_classes.append("hide-executed")

    workflow_display = display_path(workflow_path)
    activity_display = display_path(activity_path) if activity_path else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(page_title)}</title>
  <link
    rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css"
    crossorigin="anonymous"
    referrerpolicy="no-referrer"
  >
  <style>
    :root {{
      --bg: #f8f9fb;
      --paper: #ffffff;
      --border: #d9dee7;
      --muted: #5d6778;
      --text: #1f2733;
      --accent: #1d4ed8;
      --accent-soft: #e8f0ff;
      --answer: #ecfdf5;
      --answer-border: #10b981;
      --thought: #f8fafc;
      --note-bg: #fff8e8;
      --note-border: #d97706;
      --code-bg: #111827;
      --code-text: #e5e7eb;
      --shadow: 0 8px 28px rgba(15, 23, 42, 0.08);
      --radius: 16px;
      --radius-sm: 10px;
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }}

    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: var(--sans);
      line-height: 1.5;
    }}
    .page {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 32px 24px 72px;
    }}
    [data-nav-anchor="true"] {{
      scroll-margin-top: 110px;
    }}
    .toolbar-shell {{
      position: sticky;
      top: 0;
      z-index: 30;
      margin: -8px 0 24px;
    }}
    .toolbar-orb {{
      display: none;
    }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      padding: 14px 18px;
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: blur(10px);
      border: 1px solid var(--border);
      border-radius: 999px;
      box-shadow: var(--shadow);
    }}
    .toolbar strong {{
      margin-right: 8px;
      font-size: 0.96rem;
    }}
    .toolbar button, .toolbar label {{
      font: inherit;
      color: var(--text);
    }}
    .toolbar button {{
      border: 1px solid var(--border);
      background: var(--paper);
      border-radius: 999px;
      padding: 8px 14px;
      cursor: pointer;
    }}
    .toolbar label {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 8px;
      cursor: pointer;
    }}
    body.toolbar-docked .toolbar-shell {{
      position: fixed;
      top: 22px;
      left: max(16px, calc((100vw - 1240px) / 2 - 92px));
      width: 72px;
      height: 78px;
      margin: 0;
      z-index: 60;
      transition: width 0.26s cubic-bezier(0.22, 1, 0.36, 1);
    }}
    body.toolbar-docked .toolbar-shell:hover,
    body.toolbar-docked .toolbar-shell:focus-within,
    body.toolbar-docked .toolbar-shell.is-expanded {{
      width: min(780px, calc(100vw - 32px));
    }}
    body.toolbar-docked .toolbar-orb {{
      position: absolute;
      top: 50%;
      left: 10px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 52px;
      height: 52px;
      border: 1px solid var(--border);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.92);
      color: var(--muted);
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
      cursor: pointer;
      z-index: 2;
      transform: translateY(-50%);
      backdrop-filter: blur(10px);
    }}
    body.toolbar-docked .toolbar-orb i {{
      display: inline-block;
      font-size: 18px;
      line-height: 1;
      color: var(--muted);
      font-style: normal;
      text-rendering: auto;
      -webkit-font-smoothing: antialiased;
      font-family: "Font Awesome 6 Free";
      font-weight: 900;
      transition: transform 0.18s ease;
    }}
    body.toolbar-docked .toolbar-orb i.fa-regular.fa-gear::before {{
      content: "\\f013";
    }}
    body.toolbar-docked .toolbar-shell:hover .toolbar-orb i,
    body.toolbar-docked .toolbar-shell:focus-within .toolbar-orb i,
    body.toolbar-docked .toolbar-shell.is-expanded .toolbar-orb i {{
      transform: rotate(30deg);
    }}
    body.toolbar-docked .toolbar {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      min-height: 78px;
      flex-wrap: nowrap;
      justify-content: flex-start;
      gap: 14px;
      padding: 18px 20px 18px 82px;
      overflow: hidden;
      white-space: nowrap;
      pointer-events: none;
      clip-path: inset(0 calc(100% - 72px) 0 0 round 999px);
      transform: translateX(0);
      transform-origin: left center;
      transition: clip-path 0.24s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.2s ease;
    }}
    body.toolbar-docked .toolbar strong,
    body.toolbar-docked .toolbar button,
    body.toolbar-docked .toolbar label {{
      flex: 0 0 auto;
    }}
    body.toolbar-docked .toolbar-shell:hover .toolbar,
    body.toolbar-docked .toolbar-shell:focus-within .toolbar,
    body.toolbar-docked .toolbar-shell.is-expanded .toolbar {{
      pointer-events: auto;
      clip-path: inset(0 0 0 0 round 999px);
    }}
    .hero {{
      margin-bottom: 24px;
      padding: 24px 26px;
      border: 1px solid var(--border);
      border-radius: calc(var(--radius) + 2px);
      background: linear-gradient(180deg, #ffffff 0%, #f7faff 100%);
      box-shadow: var(--shadow);
    }}
    .hero h1 {{
      margin: 0 0 8px;
      font-size: 2rem;
      line-height: 1.15;
    }}
    .hero p {{
      margin: 0;
      color: var(--muted);
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
      margin: 22px 0 24px;
    }}
    .summary-layout {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin: 22px 0 24px;
      align-items: stretch;
    }}
    .summary-card {{
      padding: 14px 16px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      background: var(--paper);
    }}
    .summary-card .label {{
      display: block;
      margin-bottom: 4px;
      font-size: 0.83rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .summary-card .value {{
      font-size: 1rem;
      font-weight: 600;
      word-break: break-word;
    }}
    .summary-card.review {{
      grid-column: span 2;
    }}
    .summary-card.wide-stack {{
      grid-column: span 3;
    }}
    .summary-card.compact-list {{
      padding: 0;
      overflow: hidden;
    }}
    .summary-list-row {{
      padding: 14px 16px;
    }}
    .summary-list-row + .summary-list-row {{
      border-top: 1px solid var(--border);
    }}
    .summary-list-row .label {{
      display: block;
      margin-bottom: 4px;
      font-size: 0.8rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .summary-list-row .value {{
      font-size: 1rem;
      font-weight: 600;
      word-break: break-word;
    }}
    .summary-card.fact-grid {{
      grid-column: span 1;
      display: grid;
      grid-template-columns: 1fr;
      gap: 0;
      align-content: start;
      padding: 0;
      overflow: hidden;
    }}
    .summary-fact {{
      padding: 14px 16px;
    }}
    .summary-fact + .summary-fact {{
      border-top: 1px solid var(--border);
    }}
    .summary-fact .label {{
      display: block;
      margin-bottom: 4px;
      font-size: 0.8rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .summary-fact .value {{
      font-size: 1rem;
      font-weight: 600;
      word-break: break-word;
    }}
    .summary-card a,
    .resource-table a {{
      color: var(--accent);
      text-decoration: underline;
      text-underline-offset: 0.14em;
      word-break: break-word;
    }}
    .note-callout {{
      margin: 0 0 20px;
      padding: 18px 20px;
      border-left: 6px solid var(--note-border);
      border-radius: var(--radius-sm);
      background: var(--note-bg);
      box-shadow: var(--shadow);
    }}
    .note-callout h3 {{
      margin: 0 0 10px;
      font-size: 1.18rem;
    }}
    .note-callout p {{
      margin: 10px 0 0;
      font-size: 1rem;
    }}
    body.hide-annotations .note-callout {{
      display: none;
    }}
    .hero-callout {{
      margin-top: 18px;
    }}
    .resource-table {{
      overflow-x: auto;
      margin: 20px 0 28px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      background: var(--paper);
      box-shadow: var(--shadow);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #f3f6fb;
      font-size: 0.86rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
    }}
    tbody tr:last-child td {{
      border-bottom: 0;
    }}
    details.log-section {{
      margin: 0 0 18px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      background: var(--paper);
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    details.log-section > summary {{
      list-style: none;
      cursor: pointer;
      padding: 20px 22px;
      background: #fbfcfe;
      border-bottom: 1px solid var(--border);
    }}
    details.log-section > summary::-webkit-details-marker {{
      display: none;
    }}
    .section-heading {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px 14px;
      align-items: baseline;
      margin-bottom: 6px;
    }}
    .section-heading h2 {{
      margin: 0;
      font-size: 1.28rem;
      line-height: 1.25;
    }}
    .section-id {{
      color: var(--muted);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .section-subtitle {{
      color: var(--muted);
      font-size: 0.94rem;
    }}
    .phase-meta {{
      font-size: 0.94rem;
      color: var(--muted);
      margin-top: 4px;
    }}
    .section-body {{
      padding: 20px 22px 24px;
    }}
    .protocol-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
    }}
    .protocol-card {{
      padding: 16px 18px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      background: var(--paper);
    }}
    .protocol-card.title {{
      grid-column: 1 / -1;
      background: #fcfdff;
    }}
    .protocol-card .label {{
      display: block;
      margin-bottom: 8px;
      font-size: 0.82rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-weight: 700;
    }}
    .protocol-card .value {{
      font-size: 0.98rem;
      line-height: 1.6;
      color: var(--text);
      word-break: break-word;
    }}
    .phase-summary {{
      margin: 0 0 18px;
      padding: 14px 16px;
      border: 1px solid #d8e4ff;
      border-radius: var(--radius-sm);
      background: var(--accent-soft);
    }}
    .phase-summary strong {{
      display: block;
      margin-bottom: 6px;
    }}
    .block {{
      margin: 0 0 16px;
      padding: 16px 18px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      background: var(--paper);
    }}
    .block:last-child {{
      margin-bottom: 0;
    }}
    .block-label {{
      margin: 0 0 10px;
      font-size: 0.82rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-weight: 700;
    }}
    .block.run-panel {{
      background: #fcfdff;
    }}
    .block.thought, .block.planning {{
      background: var(--thought);
      border-color: #d7dfeb;
    }}
    .block.execution_logs {{
      background: #fefefe;
    }}
    .block.final_answer {{
      background: var(--answer);
      border-color: var(--answer-border);
      box-shadow: inset 0 0 0 1px rgba(16, 185, 129, 0.08);
    }}
    .block.stats {{
      background: #fafbfd;
      color: var(--muted);
    }}
    .block.code, .block.executed_code {{
      background: var(--code-bg);
      border-color: #1f2937;
      color: var(--code-text);
    }}
    body.hide-code .block.code {{
      display: none;
    }}
    body.hide-executed .block.executed_code {{
      display: none;
    }}
    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      overflow-wrap: anywhere;
      font-size: 0.94rem;
      font-family: var(--mono);
    }}
    .block.thought pre,
    .block.planning pre,
    .block.run-panel pre,
    .block.execution_logs pre {{
      font-family: var(--sans);
      font-size: 0.98rem;
    }}
    {PYGMENTS_CSS}
    .footer-meta {{
      margin-top: 28px;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .nav-rail {{
      position: fixed;
      top: 50%;
      left: max(16px, calc((100vw - 1240px) / 2 - 74px));
      display: flex;
      flex-direction: column;
      gap: 10px;
      transform: translateY(-50%);
      z-index: 45;
    }}
    .nav-button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 46px;
      height: 46px;
      padding: 0 14px;
      border: 1px solid var(--border);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.9);
      color: var(--muted);
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
      backdrop-filter: blur(10px);
      cursor: pointer;
      font: inherit;
      font-weight: 600;
      transition: transform 0.16s ease, background 0.16s ease, color 0.16s ease, opacity 0.16s ease;
    }}
    .nav-button:hover:not(:disabled) {{
      transform: translateY(-1px);
      background: rgba(255, 255, 255, 0.98);
      color: var(--text);
    }}
    .nav-button.arrow {{
      font-size: 1.2rem;
      padding: 0;
    }}
    .nav-button:disabled {{
      opacity: 0.45;
      cursor: default;
      transform: none;
    }}
    code.inline {{
      font-family: var(--mono);
      font-size: 0.92em;
      background: #eef2f8;
      padding: 0.12rem 0.34rem;
      border-radius: 6px;
    }}
    @media (max-width: 1120px) {{
      .summary-layout {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .summary-card.review {{
        grid-column: 1 / -1;
      }}
      body.toolbar-docked .toolbar-shell {{
        left: 16px;
      }}
      .nav-rail {{
        left: 16px;
      }}
    }}
    @media (max-width: 860px) {{
      .summary-layout,
      .summary-grid,
      .protocol-grid {{
        grid-template-columns: 1fr;
      }}
      .protocol-card.title {{
        grid-column: auto;
      }}
      body.toolbar-docked .toolbar-shell {{
        top: 14px;
        left: 12px;
        width: 64px;
        height: 64px;
      }}
      body.toolbar-docked .toolbar-shell:hover,
      body.toolbar-docked .toolbar-shell:focus-within,
      body.toolbar-docked .toolbar-shell.is-expanded {{
        width: calc(100vw - 24px);
      }}
      body.toolbar-docked .toolbar-orb {{
        left: 9px;
        width: 46px;
        height: 46px;
      }}
      body.toolbar-docked .toolbar-orb i {{
        font-size: 16px;
      }}
      body.toolbar-docked .toolbar {{
        min-height: 64px;
        padding: 14px 16px 14px 72px;
        border-radius: 28px;
        clip-path: inset(0 calc(100% - 64px) 0 0 round 28px);
      }}
      .nav-rail {{
        left: 12px;
      }}
      .nav-button {{
        min-width: 42px;
        height: 42px;
      }}
    }}
  </style>
</head>
<body class="{' '.join(body_classes)}">
  <div class="page">
    <div class="toolbar-shell" id="toolbar-shell">
      <button type="button" class="toolbar-orb" id="toolbar-orb" aria-label="Open display controls">
        <i class="fa-regular fa-gear" aria-hidden="true"></i>
      </button>
      <div class="toolbar" id="toolbar-panel">
        <strong>Display</strong>
        {('<label><input type="checkbox" id="toggle-annotations"> Show annotations</label>' if has_annotations else '')}
        <label><input type="checkbox" id="toggle-code" {'checked' if not hide_code_default else ''}> Show code</label>
        <label><input type="checkbox" id="toggle-executed" {'checked' if not hide_executed_default else ''}> Show executed code</label>
        <button type="button" id="toggle-sections">Collapse all sections</button>
      </div>
    </div>

    <section class="hero">
      <h1>{escape(page_title)}</h1>
      <p>
        Source workflow: <code class="inline">{escape(workflow_display)}</code>
        {"<br>Activity enrichment: <code class='inline'>" + escape(activity_display) + "</code>" if activity_path else ""}
      </p>
      {hero_html}
    </section>

    {render_summary_grid(summary_items)}
    {resource_table_html}
    {protocol_html}

    <details class="log-section" open id="nav-intro" data-nav-anchor="true" data-nav-label="Intro">
      <summary>
        <div class="section-heading">
          <span class="section-id">intro</span>
          <h2>Intro</h2>
        </div>
        <div class="section-subtitle">Run metadata and task input</div>
      </summary>
      <div class="section-body">
        {intro_blocks_html}
      </div>
    </details>

    {section_cards}

    <div class="footer-meta">
      Generated by <code class="inline">bastirr/scripts/render_workflow_presentation.py</code>.
    </div>
  </div>

  <div class="nav-rail" aria-label="Presentation navigation">
    <button type="button" class="nav-button" id="back-to-top" title="Back to top">Top</button>
    <button type="button" class="nav-button arrow" id="nav-prev" title="Previous section or step" aria-label="Previous section or step">↑</button>
    <button type="button" class="nav-button arrow" id="nav-next" title="Next section or step" aria-label="Next section or step">↓</button>
    <button type="button" class="nav-button" id="go-to-end" title="Go to end of run">End</button>
  </div>

  <script>
    const body = document.body;
    const toolbarShell = document.getElementById("toolbar-shell");
    const toolbarOrb = document.getElementById("toolbar-orb");
    const toggleAnnotations = document.getElementById("toggle-annotations");
    const toggleCode = document.getElementById("toggle-code");
    const toggleExecuted = document.getElementById("toggle-executed");
    const toggleSections = document.getElementById("toggle-sections");
    const backToTopButton = document.getElementById("back-to-top");
    const navPrevButton = document.getElementById("nav-prev");
    const navNextButton = document.getElementById("nav-next");
    const goToEndButton = document.getElementById("go-to-end");
    const sections = document.querySelectorAll("details.log-section");
    const navAnchors = Array.from(document.querySelectorAll('[data-nav-anchor="true"]'));
    let dockThreshold = 0;
    let activeNavIndex = 0;

    const updateToolbarDocking = () => {{
      const shouldDock = window.scrollY > dockThreshold;
      body.classList.toggle("toolbar-docked", shouldDock);
      if (!shouldDock) {{
        toolbarShell.classList.remove("is-expanded");
      }}
    }};

    const recomputeDockThreshold = () => {{
      const wasDocked = body.classList.contains("toolbar-docked");
      body.classList.remove("toolbar-docked");
      const shellTop = toolbarShell.getBoundingClientRect().top + window.scrollY;
      dockThreshold = shellTop + 28;
      if (!wasDocked) {{
        toolbarShell.classList.remove("is-expanded");
      }}
      updateToolbarDocking();
    }};

    if (toggleAnnotations) {{
      body.classList.toggle("hide-annotations", !toggleAnnotations.checked);
      toggleAnnotations.addEventListener("change", () => {{
        body.classList.toggle("hide-annotations", !toggleAnnotations.checked);
      }});
    }}

    toggleCode.addEventListener("change", () => {{
      body.classList.toggle("hide-code", !toggleCode.checked);
    }});

    toggleExecuted.addEventListener("change", () => {{
      body.classList.toggle("hide-executed", !toggleExecuted.checked);
    }});

    const allSectionsExpanded = () => Array.from(sections).every((section) => section.open);
    const updateSectionToggleLabel = () => {{
      toggleSections.textContent = allSectionsExpanded()
        ? "Collapse all sections"
        : "Expand all sections";
    }};
    const waypointLabel = (element) => element?.dataset?.navLabel || "";
    const ensureTargetVisible = (element) => {{
      const parentSection = element.closest("details.log-section");
      if (parentSection) {{
        parentSection.open = true;
      }}
    }};
    const scrollToAnchor = (index) => {{
      if (index < 0 || index >= navAnchors.length) {{
        return;
      }}
      const target = navAnchors[index];
      ensureTargetVisible(target);
      target.scrollIntoView({{ behavior: "smooth", block: "start" }});
    }};
    const updateNavButtons = () => {{
      if (!navAnchors.length) {{
        navPrevButton.disabled = true;
        navNextButton.disabled = true;
        return;
      }}
      activeNavIndex = 0;
      const threshold = window.scrollY + 130;
      navAnchors.forEach((anchor, index) => {{
        const top = anchor.getBoundingClientRect().top + window.scrollY;
        if (top <= threshold) {{
          activeNavIndex = index;
        }}
      }});
      navPrevButton.disabled = activeNavIndex <= 0;
      navNextButton.disabled = activeNavIndex >= navAnchors.length - 1;
      navPrevButton.title = navPrevButton.disabled
        ? "No previous section or step"
        : "Previous: " + waypointLabel(navAnchors[activeNavIndex - 1]);
      navNextButton.title = navNextButton.disabled
        ? "No next section or step"
        : "Next: " + waypointLabel(navAnchors[activeNavIndex + 1]);
    }};

    toggleSections.addEventListener("click", () => {{
      const expand = !allSectionsExpanded();
      sections.forEach((section, index) => {{
        section.open = expand ? true : index === 0;
      }});
      updateSectionToggleLabel();
    }});

    sections.forEach((section) => {{
      section.addEventListener("toggle", updateSectionToggleLabel);
    }});

    toolbarOrb.addEventListener("click", (event) => {{
      if (!body.classList.contains("toolbar-docked")) {{
        return;
      }}
      event.stopPropagation();
      toolbarShell.classList.toggle("is-expanded");
    }});

    document.addEventListener("click", (event) => {{
      if (!toolbarShell.contains(event.target)) {{
        toolbarShell.classList.remove("is-expanded");
      }}
    }});

    document.addEventListener("keydown", (event) => {{
      if (event.key === "Escape") {{
        toolbarShell.classList.remove("is-expanded");
      }}
    }});

    backToTopButton.addEventListener("click", () => {{
      window.scrollTo({{ top: 0, behavior: "smooth" }});
    }});

    goToEndButton.addEventListener("click", () => {{
      window.scrollTo({{
        top: document.documentElement.scrollHeight,
        behavior: "smooth",
      }});
    }});

    navPrevButton.addEventListener("click", () => {{
      scrollToAnchor(activeNavIndex - 1);
    }});

    navNextButton.addEventListener("click", () => {{
      scrollToAnchor(activeNavIndex + 1);
    }});

    window.addEventListener("scroll", () => {{
      updateToolbarDocking();
      updateNavButtons();
    }}, {{ passive: true }});
    window.addEventListener("resize", recomputeDockThreshold);
    window.addEventListener("load", recomputeDockThreshold);
    updateSectionToggleLabel();
    updateNavButtons();
    recomputeDockThreshold();
  </script>
</body>
</html>
"""


def render_summary_grid(summary_items: dict[str, str]) -> str:
    if not summary_items:
        return ""

    activity_keys = {
        "Review",
        "Date",
        "Duration",
        "Total tokens",
        "Review URL",
        "Dataset split",
        "Studies",
    }
    if activity_keys.issubset(summary_items.keys()):
        return render_activity_summary(summary_items)

    cards = []
    for key, value in summary_items.items():
        cards.append(
            f"""<div class="summary-card">
  <span class="label">{escape(key)}</span>
  <span class="value">{render_inline_html(value)}</span>
</div>"""
        )
    return f'<section class="summary-grid">\n' + "\n".join(cards) + "\n</section>"


def render_activity_summary(summary_items: dict[str, str]) -> str:
    review = summary_items.get("Review", "")
    total_tokens = summary_items.get("Total tokens", "")
    review_url = summary_items.get("Review URL", "")
    primary_stack_fields = [
        ("Review", summary_items.get("Review", "")),
        ("Review URL", summary_items.get("Review URL", "")),
        ("Total tokens", summary_items.get("Total tokens", "")),
    ]
    secondary_stack_fields = [
        ("Date", summary_items.get("Date", "")),
        ("Duration", summary_items.get("Duration", "")),
        ("Dataset split", summary_items.get("Dataset split", "")),
        ("Studies", summary_items.get("Studies", "")),
    ]

    primary_stack_rows = "\n".join(
        f"""<div class="summary-list-row">
  <span class="label">{escape(label)}</span>
  <span class="value">{render_inline_html(value)}</span>
</div>"""
        for label, value in primary_stack_fields
        if value
    )
    secondary_fact_rows = "\n".join(
        f"""<div class="summary-fact">
  <span class="label">{escape(label)}</span>
  <span class="value">{render_inline_html(value)}</span>
</div>"""
        for label, value in secondary_stack_fields
        if value
    )

    cards = [
        f"""<div class="summary-card compact-list wide-stack">
  {primary_stack_rows}
</div>""",
    ]

    if secondary_fact_rows:
        cards.append(
            f"""<div class="summary-card fact-grid">
  {secondary_fact_rows}
</div>"""
        )

    extra_items = [
        (key, value)
        for key, value in summary_items.items()
        if key
        not in {
            "Review",
            "Date",
            "Duration",
            "Total tokens",
            "Review URL",
            "Dataset split",
            "Studies",
        }
    ]
    for key, value in extra_items:
        cards.append(
            f"""<div class="summary-card">
  <span class="label">{escape(key)}</span>
  <span class="value">{render_inline_html(value)}</span>
</div>"""
        )

    return f'<section class="summary-layout">\n' + "\n".join(cards) + "\n</section>"


def render_resource_table(activity: ActivityData | None) -> str:
    if not activity or not activity.resource_rows:
        return ""

    headers_html = "".join(f"<th>{escape(header)}</th>" for header in activity.resource_headers)
    rows_html = []
    for row in activity.resource_rows:
        cells = "".join(f"<td>{render_inline_html(cell)}</td>" for cell in row)
        rows_html.append(f"<tr>{cells}</tr>")

    return f"""
<section class="resource-table">
  <table>
    <thead><tr>{headers_html}</tr></thead>
    <tbody>
      {''.join(rows_html)}
    </tbody>
  </table>
</section>
"""


def render_protocol_section(protocol: ReviewProtocol | None) -> str:
    if not protocol:
        return ""

    cards = []
    fields = [
        ("Review Title", protocol.title, "title"),
        ("Objective", protocol.objective, ""),
        ("Background", protocol.background, ""),
        ("Selection Criteria", protocol.selection_criteria, ""),
    ]
    for label, value, extra_class in fields:
        if not value:
            continue
        class_attr = "protocol-card" if not extra_class else f"protocol-card {extra_class}"
        cards.append(
            f"""<div class="{class_attr}">
  <span class="label">{escape(label)}</span>
  <div class="value">{render_inline_html(value)}</div>
</div>"""
        )

    if not cards:
        return ""

    return f"""
<details class="log-section" open>
  <summary>
    <div class="section-heading">
      <span class="section-id">protocol</span>
      <h2>Review Protocol</h2>
    </div>
    <div class="section-subtitle">Title, objective, background, and selection criteria retrieved from the source review</div>
  </summary>
  <div class="section-body">
    <div class="protocol-grid">
      {''.join(cards)}
    </div>
  </div>
</details>
"""


def block_nav_metadata(section: Section, block: Block, block_index: int) -> tuple[str, str]:
    if block.kind != "raw_output":
        return "", ""

    match = STEP_MARKER_RE.search(block.content)
    if not match:
        return "", ""

    step_number = match.group(1)
    phase_label = section.section_id.upper() if section.section_id else (section.display_title or section.raw_title)
    block_id = f"nav-{section.section_id or 'section'}-step-{step_number}-{block_index}"
    nav_label = f"{phase_label} · Step {step_number}"
    attrs = (
        f' id="{escape(block_id)}"'
        f' data-nav-anchor="true"'
        f' data-nav-label="{escape(nav_label)}"'
    )
    return attrs, nav_label


def render_section(section: Section) -> str:
    summary_html = ""
    if section.phase_summary:
        label = escape(section.phase_meta) if section.phase_meta else "Activity Summary"
        summary_html = (
            f'<div class="phase-summary"><strong>{label}</strong>'
            f'<div>{escape(section.phase_summary)}</div></div>'
        )

    note_html = render_annotation(section.annotation) if section.annotation else ""
    blocks_html = "\n".join(render_block(block) for block in section.blocks)
    subtitle = escape(section.subtitle) if section.subtitle else ""
    meta = escape(section.phase_meta) if section.phase_meta else ""

    section_nav_label = section.section_id.upper() if section.section_id else (section.display_title or section.raw_title)
    blocks_html_parts: list[str] = []
    for index, block in enumerate(section.blocks):
        attrs, _ = block_nav_metadata(section, block, index)
        blocks_html_parts.append(render_block(block, extra_attrs=attrs))
    blocks_html = "\n".join(blocks_html_parts)

    return f"""
<details class="log-section" open id="nav-{escape(section.section_id or section.raw_title.lower().replace(' ', '-'))}" data-nav-anchor="true" data-nav-label="{escape(section_nav_label)}">
  <summary>
    <div class="section-heading">
      <span class="section-id">{escape(section.section_id)}</span>
      <h2>{escape(section.display_title or section.raw_title)}</h2>
    </div>
    {f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ''}
    {f'<div class="phase-meta">{meta}</div>' if meta else ''}
  </summary>
  <div class="section-body">
    {note_html}
    {summary_html}
    {blocks_html}
  </div>
</details>
"""


def render_annotation(annotation: dict | None, extra_class: str = "") -> str:
    if not annotation:
        return ""

    title = annotation.get("title", "Presenter Note")
    body = annotation.get("body", [])
    if isinstance(body, str):
        body = [body]
    paragraphs = "\n".join(f"<p>{escape(str(paragraph))}</p>" for paragraph in body if str(paragraph).strip())
    class_attr = "note-callout" if not extra_class else f"note-callout {extra_class}"
    return f'<aside class="{class_attr}"><h3>{escape(str(title))}</h3>{paragraphs}</aside>'


def render_block(block: Block, extra_attrs: str = "") -> str:
    label = escape(block.title or block.kind.replace("_", " ").title())
    if block.kind in {"code", "executed_code"}:
        content = highlight_python(block.content)
        pre_class = ' class="code-content"'
    else:
        content = escape(format_json_if_possible(block.content))
        pre_class = ""
    return (
        f'<div class="block {escape(block.kind)}"{extra_attrs}>'
        f'<div class="block-label">{label}</div>'
        f'<pre{pre_class}>{content}</pre>'
        f"</div>"
    )


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path | None, Path | None, Path]:
    workflow = Path(args.workflow).expanduser().resolve()
    if not workflow.exists():
        raise FileNotFoundError(f"Workflow log not found: {workflow}")

    if args.activity:
        if args.activity.strip().lower() == "none":
            activity = None
        else:
            activity = Path(args.activity).expanduser().resolve()
    else:
        sibling = workflow.with_name("activity.md")
        activity = sibling if sibling.exists() else None

    annotations = Path(args.annotations).expanduser().resolve() if args.annotations else None

    if args.output:
        output = Path(args.output).expanduser().resolve()
    else:
        output = workflow.with_name("workflow_presentation.html")

    return workflow, activity, annotations, output


def main() -> None:
    args = parse_args()
    workflow_path, activity_path, annotations_path, output_path = resolve_paths(args)

    workflow_text = read_text(workflow_path)
    sections = parse_workflow_sections(workflow_text)
    annotations = AnnotationData() if args.disable_annotations else parse_annotations(annotations_path)
    activity = parse_activity_md(activity_path)
    protocol = parse_review_protocol(workflow_text)
    enrich_sections(sections, activity, annotations)

    page_title = normalize_title(workflow_path, args.title)
    html_doc = render_html(
        page_title=page_title,
        workflow_path=workflow_path,
        activity_path=activity_path,
        sections=sections,
        activity=activity,
        annotations=annotations,
        protocol=protocol,
        hide_code_default=parse_bool(args.hide_code_default),
        hide_executed_default=parse_bool(args.hide_executed_code_default),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_doc, encoding="utf-8")
    print(f"Wrote presentation HTML to {output_path}")


if __name__ == "__main__":
    main()
