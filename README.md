# Mentor — Multi-Agent Systematic Review Assistant

Mentor is a scaffolding implementation of a multi-agent architecture designed to automate systematic reviews. Built using the [smolagents](https://huggingface.co/docs/smolagents/) framework, it orchestrates specialized agents over a review protocol and candidate studies.

- Production package: `src/` (import as `mentor`)
- Screening benchmarks / Cochrane suites: [`experiments/README.md`](experiments/README.md)
- Mentor outputs: `data/mentor/output/` (gitignored)

## Architecture

```
                      ┌──────────────────────┐
                      │     Orchestrator     │
                      │      (Manager)       │
                      └──────────┬───────────┘
           ┌─────────────┬───────┴───────┬─────────────┐
           │             │               │             │
    ┌──────▼──────┐ ┌────▼─────┐  ┌──────▼──────┐ ┌────▼──────┐
    │  Librarian  │ │Gatekeeper│  │    Miner    │ │   Critic  │
    │  (Search)   │ │ (Screen) │  │  (Extract)  │ │(Synthesize│
    └─────────────┘ └──────────┘  └─────────────┘ └───────────┘
```

The Orchestrator manages the four specialists and only sees the review
protocol (title, objective, background, selection criteria)—not the
candidate study list. Studies live in a shared store the Librarian
searches, so the manager cannot pre-screen during planning and the same
path can later use a real database.

**Flow:**
1. **Librarian** — finds candidate studies for the review
2. **Gatekeeper** — includes or excludes each study against the criteria
3. **Miner** — extracts structured evidence from included abstracts
4. **Critic** — judges quality and writes a citation-backed narrative
5. **Orchestrator** — assembles the final report and evidence artifacts

## Setup

Prerequisites: Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
# 1. Install the package (editable) and lockfile deps
uv sync

# Optional extras
uv sync --extra experiments           # Streamlit dashboard + Plotly/matplotlib plots
uv sync --extra litellm               # only if MENTOR_MODEL_BACKEND=litellm / --backend litellm
uv sync --extra dev                   # pytest
uv sync --extra experiments --extra litellm --extra dev   # everything

# 2. Configure credentials (usually just the API key)
cp .env.example .env
# Set MENTOR_API_KEY in .env to your OpenRouter API key (sk-or-v1-…).
# That is enough for --profile / suite runs; catalogue profiles already set the OpenRouter base URL.
```

All commands below assume you are at the repository root. Prefer `uv run …` so the project environment is used automatically.

---

## Running the workflow

The production CLI runs the 5-agent pipeline (Librarian → Gatekeeper → Miner → Critic)
for **one** systematic review JSON file.

### Quick start (screening-only + local search)

Use a review JSON that already lists candidate studies, and keep search local
(no external search i.e., in BIP or PubMed). Example file:
[`data/mentor/input/reviews/cotrimoxazole_hiv_cd003508.json`](data/mentor/input/reviews/cotrimoxazole_hiv_cd003508.json).

In `.env` (see [`.env.example`](.env.example)):

```bash
MENTOR_API_KEY=sk-or-v1-...   # your OpenRouter key
SEARCH_SOURCES=local          # default — searches studies in the review JSON only
```

Profiles: keys in [`src/config/model_profiles.json`](src/config/model_profiles.json)
(`uv run mentor --list-profiles`). Explicit-model alternative:
[Model / backend options](#model--backend-options) and
[`src/config/README.md`](src/config/README.md).

```bash
uv run mentor --review data/mentor/input/reviews/cotrimoxazole_hiv_cd003508.json \
  --profile qwen3.5_27b
```

Field reference — `screening-only` (`studies` required):

```json
{
  "mode": "screening-only",
  "title": "...",
  "objective": "...",
  "background": "...",
  "selection_criteria": "...",
  "studies": [
    {"study_index": 1, "title": "...", "abstract": "..."},
    {"study_index": 2, "title": "...", "abstract": "..."}
  ]
}
```

### Full mode with external search (i.e., BIP / PubMed)

When the Librarian should retrieve candidates from external search (instead of a
preloaded `studies` list), use a **protocol-only** review JSON (`mode: full`,
no `studies`) and enable BIP and/or PubMed in `.env`.

Example JSON:
[`data/mentor/input/reviews/cotrimoxazole_hiv_cd003508_full.json`](data/mentor/input/reviews/cotrimoxazole_hiv_cd003508_full.json).

Field reference — `full` (default if `mode` is omitted; no `studies`):

```json
{
  "mode": "full",
  "title": "...",
  "objective": "...",
  "background": "...",
  "selection_criteria": "..."
}
```

In `.env`, change search sources and (for BIP) set a real auth token:

```bash
# Comma-separated: bip, pubmed
SEARCH_SOURCES=bip,pubmed

SEARCH_BIP_MCP_URL=https://bip-mcp.imsi.athenarc.gr/mcp
# Create a token at https://bip.imsi.athenarc.gr/site/settings
SEARCH_BIP_AUTH_TOKEN=your_bip_token

SEARCH_PUBMED_MCP_URL=https://pubmed-mcp.imsi.athenarc.gr/mcp
```

Then run:

```bash
uv run mentor --review data/mentor/input/reviews/cotrimoxazole_hiv_cd003508_full.json \
  --profile qwen3.5_27b
```

Notes:

- `local` alone only sees studies already in the JSON — useless for `mode: full`
  unless you also enable `bip` and/or `pubmed`.
- BIP requires `SEARCH_BIP_AUTH_TOKEN` (not the placeholder `example_token`).
- You can use `SEARCH_SOURCES=bip,pubmed` without `local` if you do not need
  the in-JSON study store.

Optional per-run prompt overrides (paths relative to the review JSON). Missing
roles use packaged defaults under `src/agents/prompts/`. Use a single
`orchestrator` key — `orchestrator.md` (full) or
`orchestrator_screening-only.md` (screening-only):

```json
{
  "prompts": {
    "gatekeeper": "./prompts/gatekeeper.md",
    "orchestrator": "./prompts/orchestrator.md",
    "librarian": "...",
    "miner": "...",
    "critic": "..."
  }
}
```

### Model / backend options

You must select a model configuration. Mentor aborts if neither option below is
set (it does not silently use a hard-coded default).

**Option A — named profile** (usual path for OpenRouter catalogue models):

```bash
uv run mentor --review review.json --profile openrouter_gpt5
# or set MENTOR_MODEL_PROFILE=openrouter_gpt5 in .env and omit --profile
```

**Option B — explicit model** (CLI and/or `.env`):

```bash
uv run mentor --review review.json --model gpt-5 --backend openai
uv run mentor --review review.json \
  --model openai/gpt-5 \
  --backend openai \
  --api-base https://openrouter.ai/api/v1
# or set MENTOR_MODEL / MENTOR_MODEL_BACKEND / MENTOR_API_BASE in .env
```

Do not combine a profile with `--model` / `--backend` / `--api-base`. You do not
need all three explicit flags—pass only what you want to override. Always set
`MENTOR_API_KEY` for OpenAI-compatible backends.

```bash
# Quieter activity.md (hide nested sub-agent steps)
uv run mentor --review review.json --profile openrouter_gpt5 --hide-subagent-steps
```

### Outputs

Each run writes under:

```text
data/mentor/output/<YYYYMMDD_HHMMSS>_<review-title>/
  report.md          # final narrative report
  evidence.json      # machine-readable screening/extraction evidence
  activity.md        # human-readable phase summary
  workflow.log       # full chronological agent trace
```

### Presentation HTML from a completed run

```bash
uv run python scripts/render_workflow_presentation.py \
  --workflow "data/mentor/output/<timestamp>_<review-title>/workflow.log"
```

Flags, annotations, and options: [`scripts/README.md`](scripts/README.md).

---

## Project Structure

```
src/                         # Mentor package (import as mentor)
├── cli.py                   # Production CLI (--review)
├── review.py                # One-review types + JSON I/O (no gold labels)
├── settings.py              # Paths, timeouts, shared MENTOR_* env defaults
├── logging/                 # workflow.log dual-write + activity.md audit trail
├── config/                  # model_profiles.json — see src/config/README.md
├── runtime/                 # RunSession, run_review API, profile resolver
├── agents/                  # Librarian, Gatekeeper, Miner, Critic, Orchestrator
│   └── prompts/             # Agent instruction .md files
└── tools/                   # Search, screening, extraction, synthesis, report tools

experiments/                 # Suites, dataset, analyze — see experiments/README.md

data/mentor/
├── input/reviews/           # Example / hand-written review JSON
└── output/                  # Single Mentor pipeline runs (gitignored)

data/experiments/            # Cochrane CSVs + suite outputs — see experiments/README.md

scripts/                     # Helpers (presentation export) — see scripts/README.md
```

## Repository Structure

| Directory | Description |
|-----------|-------------|
| `src/` | Mentor package root (setuptools maps it to import `mentor`). |
| `experiments/` | Suites, Cochrane dataset loaders, analyze/dashboards ([docs](experiments/README.md)). |
| `data/mentor/` | Mentor review JSON inputs + single-run outputs. |
| `data/experiments/` | Cochrane dataset + suite outputs (owned by experiments). |
| `resources/architecture/` | Design spec for the multi-agent architecture (includes MCP strategy). |
| `resources/vaccine_indicators_demo/` | Separate LLM pipeline for medical evidence extraction. |
| `tests/` | Pytest suite for mentor + experiment harness. |

## Model configuration

Set `MENTOR_API_KEY` in `.env`, then choose **either** a profile
(`--profile` / `MENTOR_MODEL_PROFILE`) **or** an explicit model
(`--model` / `--backend` / `--api-base`, or the matching `MENTOR_*` env vars).
If neither is defined, the CLI exits with an error listing those options.

Catalogue, profile schema, OpenRouter / LiteLLM / Ollama details:
[`src/config/README.md`](src/config/README.md).

## MCP paper search (BIP + PubMed)

For env setup and which review JSON to use, see
[Full mode + BIP / PubMed search](#full-mode--bip--pubmed-search) above.

## CLI Arguments (full workflow)

```bash
uv run mentor --review PATH [OPTIONS]

Options:
  --review PATH        Required. One-review JSON (no gold labels)
  --profile KEY        Profile from model_profiles.json (mutually exclusive
                       with --model/--backend/--api-base)
  --model MODEL_ID     Shared model id (optional; env default if omitted)
  --backend BACKEND    openai (default) or transformers
  --api-base URL       OpenAI-compatible API base URL
  --batch-size N       Studies per Gatekeeper call (omit=all, 1=single-study)
  --list-profiles      List model profiles and exit
  --hide-subagent-steps
                       Hide sub-agent step details in activity.md

Model flags are optional. Use --profile XOR --model/--backend/--api-base
(any subset); otherwise fall back to MENTOR_* env defaults. Pipeline mode
comes from the review JSON ``mode`` field (full | screening-only).
```


## Configuration Reference

Settings are split by domain:

- [`src/settings.py`](src/settings.py) — paths, timeouts, shared env defaults
- [`src/runtime/models.py`](src/runtime/models.py) — `create_model` / resolve helpers
- [`src/tools/search/settings.py`](src/tools/search/settings.py) — search sources / MCP
- Experiments dataset / suite paths: [`experiments/README.md`](experiments/README.md)

Key env settings:

| Setting | Source | Default | Description |
|---------|--------|---------|-------------|
| `MENTOR_API_KEY` | `.env` | — | API key for OpenAI-compatible backends (including OpenRouter) |
| `MENTOR_MODEL_BACKEND` | `.env` | `openai` | Model backend: `openai` or `litellm` |
| `MENTOR_MODEL` | `.env` | `gpt-5` | Model identifier (provider-prefixed for LiteLLM) |
| `MENTOR_API_BASE` | `.env` | — | API base URL for OpenAI-compatible or local servers |
| `MENTOR_MODEL_PROFILE` | `.env` | — | Runtime model profile key |
| `MENTOR_MODELS_CONFIG` | `.env` | `src/config/model_profiles.json` | Alternate model catalogue file |
| `MENTOR_EXECUTOR_TIMEOUT` | `.env` | `500` | Max seconds per code-execution step |
| `SEARCH_SOURCES` | `.env` | `local` | Comma-separated search sources: `local`, `bip`, `pubmed` |
| `SEARCH_BIP_MCP_URL` | `.env` | `https://bip-mcp.imsi.athenarc.gr/mcp` | BIP MCP endpoint (used when `bip` in `SEARCH_SOURCES`) |
| `SEARCH_BIP_AUTH_TOKEN` | `.env` | — | Bearer token for BIP MCP search endpoint (required for auth) |
| `SEARCH_PUBMED_MCP_URL` | `.env` | `https://pubmed-mcp.imsi.athenarc.gr/mcp` | PubMed MCP endpoint (used when `pubmed` in `SEARCH_SOURCES`) |
| `OUTPUT_DIR` (mentor) | auto | `data/mentor/output/` | Mentor single-run artifacts |
