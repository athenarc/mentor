# Scripts

## Workflow presentation exporter

`render_workflow_presentation.py` builds a presentation-oriented HTML view of a
completed Mentor run.

- **Primary input**: `workflow.log`
- **Optional enrichment**: sibling `activity.md`
- **Output**: self-contained `workflow_presentation.html`

Useful for demos, reviews, and handovers. It keeps the chronological run trace
while making it easier to present:

- run metadata and protocol summaries
- phase summaries from `activity.md`
- code and executed-code toggles
- optional presenter annotations
- phase and inline-step navigation

Requires the `scripts` extra for syntax highlighting (`uv sync --extra scripts`).

### Basic usage

From the repository root:

```bash
uv run python scripts/render_workflow_presentation.py \
  --workflow "data/mentor/output/<timestamp>_<review-title>/workflow.log"
```

Disable annotations entirely:

```bash
uv run python scripts/render_workflow_presentation.py \
  --workflow "data/mentor/output/<timestamp>_<review-title>/workflow.log" \
  --disable-annotations
```

Use a specific annotations file and output path:

```bash
uv run python scripts/render_workflow_presentation.py \
  --workflow "data/mentor/output/<timestamp>_<review-title>/workflow.log" \
  --annotations "data/mentor/output/<timestamp>_<review-title>/workflow_presentation_annotations.json" \
  --output "data/mentor/output/<timestamp>_<review-title>/presentation.html"
```

Workflow-only mode without `activity.md` enrichment:

```bash
uv run python scripts/render_workflow_presentation.py \
  --workflow "data/mentor/output/<timestamp>_<review-title>/workflow.log" \
  --activity none
```

### CLI options

```text
uv run python scripts/render_workflow_presentation.py [OPTIONS]

Options:
  --workflow PATH                  Path to workflow.log (required)
  --activity PATH|none             Optional activity.md path; defaults to sibling file if present
  --annotations PATH               Optional annotations JSON
  --disable-annotations            Ignore annotations even if provided
  --output PATH                    Output HTML path; defaults to workflow_presentation.html beside workflow.log
  --title TEXT                     Override the page title
  --hide-code-default true|false   Hide raw code blocks on initial load (default: true)
  --hide-executed-code-default true|false
                                   Hide executed-code blocks on initial load (default: true)
```

### Annotation file

Optional sidecar JSON for presenter notes:

```json
{
  "hero": {
    "title": "What to notice",
    "body": [
      "The orchestrator only sees the protocol, not the candidate studies."
    ]
  },
  "sections": {
    "phase-2": {
      "title": "Search handoff",
      "body": [
        "This phase shows the librarian search and the candidate handoff to screening."
      ]
    }
  }
}
```

Navigation in the exported HTML follows the run structure:

- `Intro`
- phase sections (`PHASE-1`, `PHASE-2`, ...)
- inline `Workflow Output` step markers inside each phase (`PHASE-2 · Step 1`, `PHASE-2 · Step 2`, ...)
