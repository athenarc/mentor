# Mentor — Multi-Agent Systematic Review Assistant

Mentor is a scaffolding implementation of a multi-agent architecture designed to automate systematic reviews. Built using the [smolagents](https://huggingface.co/docs/smolagents/) framework, it orchestrates specialized agents to process research from the Cochrane dataset.

- Production package: `src/mentor/`
- Screening benchmarks and related CLIs: `src/experiments/`
- Run outputs: `data/output/` (gitignored)

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
    └──────┬──────┘ └────┬─────┘  └──────┬──────┘ └────┬──────┘
           │             │               │             │
      search_studies  screen_studies batch_extract  synthesize
      get_protocol                   extract_from   assess_quality
```

All four sub-agents are **managed agents** of the Orchestrator. The Orchestrator also has its own utility tools: `format_report`, `save_evidence_json`, `extract_included_studies`, and `get_candidates_json`.

**Data flow:** The Orchestrator delegates to agents in sequence:
1. **Librarian** — retrieves candidate studies from a module-level data store (simulating a database query)
2. **Orchestrator** calls `get_candidates_json()` to obtain the structured candidate data
3. **Gatekeeper** — screens each study (INCLUDE/EXCLUDE) against selection criteria
4. **Miner** — extracts PICO evidence from included studies' abstracts
5. **Critic** — assesses quality and synthesizes a citation-backed narrative
6. **Orchestrator** calls `format_report()` and `save_evidence_json()` to produce outputs

> **Key design decision:** The Orchestrator's task text contains *only* the review protocol (title, objective, background, selection criteria) — never the candidate studies. Studies are loaded into a module-level store before the pipeline starts and accessed by the Librarian's tools. This prevents the Orchestrator from pre-screening studies during its planning phase and future-proofs the architecture for real database search.

## Setup

Prerequisites: Python 3.10+, [uv](https://docs.astral.sh/uv/), and the Cochrane dataset checkout.

```bash
# 1. Install the package (editable) and lockfile deps
uv sync

# Optional extras
uv sync --extra experiments           # Streamlit dashboard + Plotly/matplotlib plots
uv sync --extra litellm               # only if MENTOR_MODEL_BACKEND=litellm / --backend litellm
uv sync --extra dev                   # pytest
uv sync --extra experiments --extra litellm --extra dev   # everything

# 2. Configure credentials
cp .env.example .env
# Edit .env — use MENTOR_* keys (formerly BASTIRR_* / SR_AGENTS_*).
# For OpenRouter-backed experiment presets you also need OPENROUTER_API_KEY.

# 3. Download the Cochrane dataset (required for workflow + experiments)
# DOI: 10.17632/7sgmg89zb6.1
cd data/input/cochrane_sr_dataset && ./download.sh && cd ../../..
```

All commands below assume you are at the repository root. Prefer `uv run …` so the project environment is used automatically.

---

## Running the full workflow

The production CLI runs the end-to-end 5-agent pipeline (Librarian → Gatekeeper → Miner → Critic) for a single Cochrane review.

### Default demo

```bash
# List reviews in a split
uv run mentor --list-reviews --split HIV_test

# Run the default demo (HIV Cotrimoxazole review on HIV_test)
uv run mentor
```

### Choose a review

```bash
# Pick a review URL + dataset split
uv run mentor \
  --split random_test \
  --review-url "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004413.pub2/full"
```

Splits: `dev`, `val`, `random_test`, `heart_test`, `HIV_test`.

### Model / backend options

```bash
# Explicit model + backend (OpenAI-compatible)
uv run mentor --model gpt-5 --backend openai

# OpenRouter-style model id + base URL
uv run mentor \
  --model openai/gpt-5 \
  --backend openai \
  --api-base https://openrouter.ai/api/v1

# Named runtime profile from src/mentor/runtime/profiles.json
uv run mentor --model-profile openrouter_gpt5

# Quieter activity.md (hide nested sub-agent steps)
uv run mentor --hide-subagent-steps
```

You can also set defaults in `.env` (`MENTOR_MODEL`, `MENTOR_MODEL_BACKEND`, `MENTOR_API_BASE`, `MENTOR_API_KEY`, `MENTOR_MODEL_PROFILE`, …). CLI flags override env for that run.

### Outputs

Each run writes under:

```text
data/output/<YYYYMMDD_HHMMSS>_<review-title>/
  report.md          # final narrative report
  evidence.json      # machine-readable screening/extraction evidence
  activity.md        # human-readable phase summary
  workflow.log       # full chronological agent trace
```

### Presentation HTML from a completed run

```bash
uv run python scripts/render_workflow_presentation.py \
  --workflow "data/output/<timestamp>_<review-title>/workflow.log"
```

See [Workflow Presentation Exporter](#workflow-presentation-exporter) for annotations and extra flags.

---

## Running experiments

Screening benchmarks live in `src/experiments/`. Setup, suites/presets, batch and
loop CLIs, outputs, helpers, Streamlit, and plots are documented in
[`src/experiments/README.md`](src/experiments/README.md).

---

## Project Structure

```
src/mentor/
├── cli.py                   # Production CLI (console script: mentor)
├── settings.py              # Paths, timeouts, shared MENTOR_* env defaults
├── logging/                 # workflow.log dual-write + activity.md audit trail
├── dataset/                 # Review models + Cochrane schema + loaders
│   └── loaders/             # e.g. cochrane_csv.py (+ more sources later)
├── runtime/                 # RunSession, model factory, profiles.json
├── agents/                  # Librarian, Gatekeeper, Miner, Critic, Orchestrator
│   └── prompts/             # Production agent instruction .md files
├── tools/                   # Search, screening, extraction, synthesis, report tools

src/experiments/
├── screening.py             # Batch Gatekeeper benchmark CLI
├── screening_loop.py        # Looped / chunked benchmark CLI
├── config/                  # suites.json + models.json registries
├── harness/                 # Runners, metrics, checkpoints
├── prompts/                 # Experiment-only agent instructions
├── streamlit_app/           # Screening benchmark dashboard pages
├── benchmark_runs_ui.py     # Streamlit entry for the dashboard
├── plot_screening_leaderboards.py  # Leaderboard chart CLI
└── sample_review_suites.py  # Dataset sampling helper

data/output/                 # All run artifacts (gitignored)

scripts/                     # Standalone helper CLIs (presentation export, etc.)
```

## Repository Structure

| Directory | Description |
|-----------|-------------|
| `src/mentor/` | Core agent package — agents, tools, config, dataset loaders, CLI. |
| `src/experiments/` | Screening benchmarks and evaluation CLIs. |
| `data/input/cochrane_sr_dataset/` | Only `download.sh` in git; fetches the five required Cochrane split CSVs. |
| `data/output/` | Run and benchmark artifacts (gitignored). |
| `resources/architecture/` | Design spec for the multi-agent architecture (includes MCP strategy). |
| `resources/vaccine_indicators_demo/` | Separate LLM pipeline for medical evidence extraction. |
| `tests/` | Pytest suite for mentor + experiment harness. |

## Current Status: Scaffolding (End-to-End Functional)

This is a **scaffolding implementation** — the agents run end-to-end and produce correct results, but with simplifications:

- **Librarian**: Returns pre-loaded studies from a module-level data store (no real PubMed/OpenAIRE search yet, but the architecture is ready for it)
- **Gatekeeper**: Screens based on title/abstract only (no full-text retrieval)
- **Miner**: Extracts from abstracts only (no PDF OCR pipeline)
- **Critic**: Synthesizes from abstract-level evidence

The pipeline has been validated on the Cotrimoxazole/HIV review (10 candidates, 1 included), achieving 10/10 screening accuracy against the Cochrane ground truth. Outputs include a structured Markdown report (`report.md`) and a machine-readable evidence file (`evidence.json`).

## Workflow Presentation Exporter

Mentor includes a presentation-oriented exporter for completed runs:

- **Script**: `scripts/render_workflow_presentation.py`
- **Primary input**: `workflow.log`
- **Optional enrichment**: sibling `activity.md`
- **Output**: self-contained `workflow_presentation.html`

The exporter is designed for demos, reviews, and handovers. It preserves the chronological run trace while making it easier to present:

- run metadata and protocol summaries
- phase summaries from `activity.md`
- code and executed-code toggles
- optional presenter annotations
- phase and inline-step navigation

### Basic usage

```bash
uv run python scripts/render_workflow_presentation.py \
  --workflow "data/output/<timestamp>_<review-title>/workflow.log"
```

Disable annotations entirely:

```bash
uv run python scripts/render_workflow_presentation.py \
  --workflow "data/output/<timestamp>_<review-title>/workflow.log" \
  --disable-annotations
```

Use a specific annotations file and output path:

```bash
uv run python scripts/render_workflow_presentation.py \
  --workflow "data/output/<timestamp>_<review-title>/workflow.log" \
  --annotations "data/output/<timestamp>_<review-title>/workflow_presentation_annotations.json" \
  --output "data/output/<timestamp>_<review-title>/presentation.html"
```

Workflow-only mode without `activity.md` enrichment:

```bash
uv run python scripts/render_workflow_presentation.py \
  --workflow "data/output/<timestamp>_<review-title>/workflow.log" \
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

The exporter supports an optional sidecar JSON file for presenter notes:

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

This makes the file suitable both for presentation and for structured walkthroughs of a Mentor run.

### Next Steps

- [ ] Find Full-text paper for existing SR dataset
- [ ] Add full-text PDF retrieval and OCR (reuse `ocr_pdf_to_markdown.py`)
- [ ] Add real search via PubMed API (MCP server)
- [ ] Evaluate and enrich the Agent Instructions based on PRISMA and GRADE Guidelines (Gatekeeper, Miner, Critic)
- [ ] Implement Expert-in-the-Loop checkpoints (smolagents `UserInputTool`)
- [ ] Add consistency checks and conflict resolution between agents
- [ ] Test on reviews with more included studies
- [ ] Add automated test suite

## Demo Review

The default demo uses a small HIV review:
- **"Cotrimoxazole prophylaxis for opportunistic infections in children with HIV infection"**
- 10 studies total (1 included, 9 excluded at screening)
- From the HIV test set of the Cochrane dataset

## Model Configuration

Mentor supports **multiple model backends** via smolagents:

### OpenAI-Compatible (default)

Use OpenAI-compatible endpoints with `OpenAIServerModel`.
This covers direct OpenAI and OpenRouter.

```bash
# Via .env: direct OpenAI
MENTOR_MODEL_BACKEND=openai
MENTOR_MODEL=gpt-5
MENTOR_API_KEY=sk-...

# Or via CLI
uv run mentor --model gpt-5
```

```bash
# Via .env: OpenRouter
MENTOR_MODEL_BACKEND=openai
MENTOR_MODEL=openai/gpt-5
MENTOR_API_BASE=https://openrouter.ai/api/v1
MENTOR_API_KEY=sk-or-v1-...
```

### Runtime Model Profiles

For reusable runtime setups, Mentor supports JSON-backed model profiles.

- Default profile file: `src/mentor/runtime/profiles.json`
- Select a profile with `MENTOR_MODEL_PROFILE=<profile-key>` or `--model-profile <profile-key>`
- Override the profile file with `MENTOR_MODEL_PROFILES_CONFIG=/absolute/path/to/profiles.json`

Profiles can define:

- a single shared model for all agents
- different models by role (`orchestrator`, `librarian`, `gatekeeper`, `miner`, `critic`)
- OpenRouter `extra_body` request configuration such as provider pinning and reasoning settings

Recommended split of responsibility:

- the profile owns non-secret runtime configuration such as `backend`, `model_id`, `api_base`, and `request_kwargs`
- environment variables provide secrets such as API keys
- env-based overrides like `api_base_env_var` or `model_id_env_var` should only be used when you intentionally want to make a profile mutable at runtime

Shared-profile example:

```bash
MENTOR_MODEL_PROFILE=openrouter_gpt5
MENTOR_API_KEY=sk-or-v1-...
MENTOR_API_BASE=https://openrouter.ai/api/v1
uv run mentor
```

Non-shared profiles use explicit agent-role keys instead of `shared`.
The supported role keys are:

- `orchestrator`
- `librarian`
- `gatekeeper`
- `miner`
- `critic`

Resolution rules:

- if `shared` is present, it is used as the default for every role
- any explicit role entry overrides `shared` for that role
- if `shared` is absent, all five role entries must be provided
- `api_key_env_vars` is checked in order, and the first non-empty env var wins

Minimal non-shared example:

```json
{
  "profiles": [
    {
      "key": "multimodel_openrouter",
      "description": "GPT-5 for coordination, DeepSeek for screening.",
      "agents": {
        "shared": {
          "backend": "openai",
          "model_id": "openai/gpt-5",
          "api_base": "https://openrouter.ai/api/v1",
          "api_key_env_vars": ["MENTOR_API_KEY"],
          "requires_api_key": true,
          "request_kwargs": {
            "extra_body": {
              "provider": {
                "order": ["openai/default"],
                "allow_fallbacks": false,
                "require_parameters": true
              },
              "reasoning": {
                "effort": "high"
              }
            }
          }
        },
        "gatekeeper": {
          "backend": "openai",
          "model_id": "deepseek/deepseek-v4-pro",
          "api_base": "https://openrouter.ai/api/v1",
          "api_key_env_vars": ["MENTOR_API_KEY"],
          "requires_api_key": true,
          "request_kwargs": {
            "extra_body": {
              "provider": {
                "order": ["deepseek"],
                "allow_fallbacks": false,
                "require_parameters": true
              },
              "reasoning": {
                "enabled": true,
                "effort": "high"
              }
            }
          }
        }
      }
    }
  ]
}
```

In that example:

- `orchestrator`, `librarian`, `miner`, and `critic` inherit the `shared` GPT-5 config
- `gatekeeper` overrides only its own model and request configuration
- the OpenRouter base URL is owned by the profile, while the API key still comes from `MENTOR_API_KEY`

To use a custom profile file:

```bash
MENTOR_MODEL_PROFILES_CONFIG=/absolute/path/to/profiles.json
MENTOR_MODEL_PROFILE=multimodel_openrouter
MENTOR_API_KEY=sk-or-v1-...
uv run mentor
```

Useful profile fields:

- `backend`: `openai`, `litellm`, or `hf-hub`
- `backend_env_var`: optional env var name that overrides `backend`
- `model_id`: default model identifier
- `model_id_env_var`: optional env var name that overrides `model_id`
- `api_base`: default API base
- `api_base_env_var`: optional env var name that overrides `api_base`
- `api_key_env_vars`: ordered list of env vars to try for the API key
- `requires_api_key`: whether Mentor should fail early if no key resolves
- `request_kwargs`: extra kwargs forwarded to the underlying `smolagents` model constructor

For OpenRouter with the OpenAI SDK compatibility path, provider routing and reasoning controls belong under `request_kwargs.extra_body`.

### Anthropic (via LiteLLM)

```bash
# Via .env
MENTOR_MODEL_BACKEND=litellm
MENTOR_MODEL=anthropic/claude-3-5-sonnet-latest
MENTOR_API_KEY=sk-ant-...

# Or via CLI
uv run mentor --backend litellm --model anthropic/claude-3-5-sonnet-latest
```

### Local Models (Ollama)

```bash
# Start Ollama server: ollama serve
# Pull model: ollama pull llama3.2

# Via .env
MENTOR_MODEL_BACKEND=litellm
MENTOR_MODEL=ollama_chat/llama3.2
MENTOR_API_BASE=http://localhost:11434

# Or via CLI
uv run mentor \
  --backend litellm \
  --model ollama_chat/llama3.2 \
  --api-base http://localhost:11434
```

### Other Providers

LiteLLM supports 100+ providers. See [LiteLLM docs](https://docs.litellm.ai/) for provider-specific model IDs:

- **Azure OpenAI**: `azure/<DEPLOYMENT_NAME>`
- **AWS Bedrock**: `bedrock/anthropic.claude-3-sonnet-20240229-v1:0`
- **Google Vertex**: `vertex_ai/gemini-pro`
- **vLLM**: Set `MENTOR_API_BASE` to your vLLM server URL

## MCP paper search (BIP + PubMed)

The Librarian can optionally call external MCP servers for additional paper
search alongside the pre-loaded Cochrane dataset:
- BIP MCP: `https://bip-mcp.imsi.athenarc.gr/mcp`
- PubMed MCP: `https://pubmed-mcp.imsi.athenarc.gr/mcp`

**Setup:**

1. Configure endpoints in `.env`:
   ```bash
   SEARCH_SOURCES=local,bip,pubmed
   SEARCH_BIP_MCP_URL=https://bip-mcp.imsi.athenarc.gr/mcp
   SEARCH_PUBMED_MCP_URL=https://pubmed-mcp.imsi.athenarc.gr/mcp
   ```
2. Set your BIP auth token (required by BIP server):
   ```bash
   SEARCH_BIP_AUTH_TOKEN=your_bip_token_here
   ```
When enabled, the Librarian gets MCP search tools (for BIP and/or PubMed):
- `search_papers_in_bip(query, page=1, page_size=20, ordering="popularity", ...)`
- `search_papers_in_pubmed(query, offset=0, limit=20, sort="relevance")`

The candidate list used by the pipeline is what the Librarian publishes via
`set_librarian_candidates(...)`.

## CLI Arguments (full workflow)

```bash
uv run mentor [OPTIONS]

Options:
  --review-url URL     Cochrane review URL to process
  --split SPLIT        Dataset split: dev, val, random_test, heart_test, HIV_test
  --model MODEL_ID     Model identifier (e.g. gpt-5, anthropic/claude-3-5-sonnet-latest)
  --backend BACKEND    Model backend: openai (default) or litellm
  --api-base URL       API base URL for local servers (e.g. http://localhost:11434)
  --model-profile KEY  Runtime model profile key from src/mentor/runtime/profiles.json
  --list-reviews       List available reviews and exit
  --hide-subagent-steps
                       Hide sub-agent step details in activity.md
```

## Configuration Reference

Settings are split by domain:

- [`src/mentor/settings.py`](src/mentor/settings.py) — paths, timeouts, shared env defaults
- [`src/mentor/runtime/models.py`](src/mentor/runtime/models.py) — `create_model` / resolve helpers
- [`src/mentor/dataset/cochrane.py`](src/mentor/dataset/cochrane.py) — Cochrane CSV paths and labels
- [`src/mentor/tools/search/settings.py`](src/mentor/tools/search/settings.py) — search sources / MCP

Key env settings:

| Setting | Source | Default | Description |
|---------|--------|---------|-------------|
| `MENTOR_API_KEY` | `.env` | — | Preferred API key for OpenAI-compatible backends |
| `OPENAI_API_KEY` | `.env` | — | Legacy fallback for direct OpenAI if `MENTOR_API_KEY` is unset |
| `MENTOR_MODEL_BACKEND` | `.env` | `openai` | Model backend: `openai` or `litellm` |
| `MENTOR_MODEL` | `.env` | `gpt-5` | Model identifier (provider-prefixed for LiteLLM) |
| `MENTOR_API_BASE` | `.env` | — | API base URL for OpenAI-compatible or local servers |
| `MENTOR_MODEL_PROFILE` | `.env` | — | Runtime model profile key |
| `MENTOR_MODEL_PROFILES_CONFIG` | `.env` | `src/mentor/runtime/profiles.json` | Alternate runtime model-profile file |
| `MENTOR_EXECUTOR_TIMEOUT` | `.env` | `500` | Max seconds per code-execution step |
| `SEARCH_SOURCES` | `.env` | `local` | Comma-separated search sources: `local`, `bip`, `pubmed` |
| `SEARCH_BIP_MCP_URL` | `.env` | `https://bip-mcp.imsi.athenarc.gr/mcp` | BIP MCP endpoint (used when `bip` in `SEARCH_SOURCES`) |
| `SEARCH_BIP_AUTH_TOKEN` | `.env` | — | Bearer token for BIP MCP search endpoint (required for auth) |
| `SEARCH_PUBMED_MCP_URL` | `.env` | `https://pubmed-mcp.imsi.athenarc.gr/mcp` | PubMed MCP endpoint (used when `pubmed` in `SEARCH_SOURCES`) |
| `DATASET_DIR` | auto | `data/input/cochrane_sr_dataset/` | Cochrane dataset directory |
