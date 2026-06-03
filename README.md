# Bastirr — Multi-Agent Systematic Review Assistant

Bastirr is a scaffolding implementation of a multi-agent architecture designed to automate systematic reviews. Built using the  [smolagents](https://huggingface.co/docs/smolagents/) framework, it orchestrates specialized agents to process research from the Cochrane dataset. The core agent code lives in the `bastirr/` package.

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
      search_studies  batch_screen   batch_extract  synthesize
      get_protocol    screen_study   extract_from   assess_quality
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

## Quick Start

```bash
# 1. Install dependencies (installs Bastirr agent requirements)
pip install -r requirements.txt

# For LiteLLM support (Anthropic, Ollama, local models):
pip install 'smolagents[litellm]'

# Optional: Install dataset analysis dependencies (for EDA notebooks)
# pip install -r systematic_review_dataset/requirements.txt

# 2. Set up API access
#    Copy the template and add your API key
cp .env.example .env
#    Then edit .env and set: BASTIRR_API_KEY=...

# 3. Ensure the dataset is downloaded
cd systematic_review_dataset && ./download_dataset.sh && cd ..

# 4. List available reviews
python3 -m bastirr.run_demo --list-reviews --split HIV_test

# 5. Run the demo (uses default HIV Cotrimoxazole review with OpenAI)
python3 -m bastirr.run_demo
```

## Project Structure

```
bastirr/
├── __init__.py              # Package docstring
├── config.py                # Configuration, paths, API keys
├── logging_utils.py         # Run logging (workflow + decision summary)
├── run_demo.py              # CLI entry point & end-to-end runner
├── requirements.txt         # Python dependencies
├── scripts/
│   ├── __init__.py          # Bastirr-specific utility scripts
│   └── render_workflow_presentation.py  # Presentation HTML exporter for completed runs
├── data/
│   └── __init__.py          # Dataset loader (SystematicReview dataclass)
├── agents/
│   ├── __init__.py          # Agent factory exports
│   ├── librarian.py         # Search & retrieval agent
│   ├── gatekeeper.py        # Screening agent
│   ├── miner.py             # Evidence extraction agent
│   ├── critic.py            # Synthesis & quality agent
│   └── orchestrator.py      # Manager agent (wires all sub-agents)
├── tools/
│   ├── __init__.py          # Tools package
│   ├── search_tools.py      # Librarian's @tool functions + module-level data store
│   ├── screening_tools.py   # Gatekeeper's @tool functions
│   ├── extraction_tools.py  # Miner's @tool functions
│   ├── synthesis_tools.py   # Critic's @tool functions
│   └── report_tools.py     # Orchestrator's @tool functions (report, evidence JSON, parsing)
└── output/                  # Run outputs (report + logs)
```

## Repository Structure

| Directory | Description |
|-----------|-------------|
| `bastirr/` | Core agent package — agents, tools, config, data loader, CLI runner, and Bastirr-specific utility scripts. |
| `systematic_review_dataset/` | Cochrane dataset (8,608 reviews, 544K studies) used as the input source for the demo. |
| `resources/architecture_docs/` | Design specs defining the 5-agent architecture, MCP integration, and Expert-in-the-Loop approach. |
| `resources/vaccine_indicators_demo/` | Separate LLM pipeline for medical evidence extraction (PDF → OCR → extraction → synthesis). |

## Current Status: Scaffolding (End-to-End Functional)

This is a **scaffolding implementation** — the agents run end-to-end and produce correct results, but with simplifications:

- **Librarian**: Returns pre-loaded studies from a module-level data store (no real PubMed/OpenAIRE search yet, but the architecture is ready for it)
- **Gatekeeper**: Screens based on title/abstract only (no full-text retrieval)
- **Miner**: Extracts from abstracts only (no PDF OCR pipeline)
- **Critic**: Synthesizes from abstract-level evidence

The pipeline has been validated on the Cotrimoxazole/HIV review (10 candidates, 1 included), achieving 10/10 screening accuracy against the Cochrane ground truth. Outputs include a structured Markdown report (`report.md`) and a machine-readable evidence file (`evidence.json`).

## Workflow Presentation Exporter

Bastirr includes a presentation-oriented exporter for completed runs:

- **Script**: `bastirr/scripts/render_workflow_presentation.py`
- **Primary input**: `workflow.log`
- **Optional enrichment**: sibling `activity.md`
- **Output**: self-contained `workflow_presentation.html`

The exporter is designed for demos, reviews, and handovers. It preserves the chronological run trace while making it easier to present:

- run metadata and protocol summaries
- phase summaries from `activity.md`
- code and executed-code toggles
- optional presenter annotations
- phase and inline-step navigation

It uses the standard project dependencies from `requirements.txt`, including `pygments` for syntax highlighting in rendered code blocks.

### Basic usage

Generate a presentation HTML file beside a completed run:

```bash
python3 -m bastirr.scripts.render_workflow_presentation \
  --workflow "bastirr/output/<timestamp>_<review-title>/workflow.log"
```

Disable annotations entirely:

```bash
python3 -m bastirr.scripts.render_workflow_presentation \
  --workflow "bastirr/output/<timestamp>_<review-title>/workflow.log" \
  --disable-annotations
```

Use a specific annotations file and output path:

```bash
python3 -m bastirr.scripts.render_workflow_presentation \
  --workflow "bastirr/output/<timestamp>_<review-title>/workflow.log" \
  --annotations "bastirr/output/<timestamp>_<review-title>/workflow_presentation_annotations.json" \
  --output "bastirr/output/<timestamp>_<review-title>/presentation.html"
```

Workflow-only mode without `activity.md` enrichment:

```bash
python3 -m bastirr.scripts.render_workflow_presentation \
  --workflow "bastirr/output/<timestamp>_<review-title>/workflow.log" \
  --activity none
```

### CLI options

```text
PYTHONPATH=. python3 -m bastirr.scripts.render_workflow_presentation [OPTIONS]

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

This makes the file suitable both for presentation and for structured walkthroughs of a Bastirr run.

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

Bastirr supports **multiple model backends** via smolagents:

### OpenAI-Compatible (default)

Use OpenAI-compatible endpoints with `OpenAIServerModel`.
This covers direct OpenAI and OpenRouter.

```bash
# Via .env: direct OpenAI
BASTIRR_MODEL_BACKEND=openai
BASTIRR_MODEL=gpt-5
BASTIRR_API_KEY=sk-...

# Or via CLI
python3 -m bastirr.run_demo --model gpt-5
```

```bash
# Via .env: OpenRouter
BASTIRR_MODEL_BACKEND=openai
BASTIRR_MODEL=openai/gpt-5
BASTIRR_API_BASE=https://openrouter.ai/api/v1
BASTIRR_API_KEY=sk-or-v1-...
```

### Runtime Model Profiles

For reusable runtime setups, Bastirr supports JSON-backed model profiles.

- Default profile file: `bastirr/runtime_config/model_profiles.json`
- Select a profile with `BASTIRR_MODEL_PROFILE=<profile-key>` or `--model-profile <profile-key>`
- Override the profile file with `BASTIRR_MODEL_PROFILES_CONFIG=/absolute/path/to/model_profiles.json`

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
BASTIRR_MODEL_PROFILE=openrouter_gpt5
BASTIRR_API_KEY=sk-or-v1-...
BASTIRR_API_BASE=https://openrouter.ai/api/v1
python3 -m bastirr.run_demo
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
          "api_key_env_vars": ["BASTIRR_API_KEY"],
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
          "api_key_env_vars": ["BASTIRR_API_KEY"],
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
- the OpenRouter base URL is owned by the profile, while the API key still comes from `BASTIRR_API_KEY`

To use a custom profile file:

```bash
BASTIRR_MODEL_PROFILES_CONFIG=/absolute/path/to/model_profiles.json
BASTIRR_MODEL_PROFILE=multimodel_openrouter
BASTIRR_API_KEY=sk-or-v1-...
python3 -m bastirr.run_demo
```

Useful profile fields:

- `backend`: `openai`, `litellm`, or `hf-hub`
- `backend_env_var`: optional env var name that overrides `backend`
- `model_id`: default model identifier
- `model_id_env_var`: optional env var name that overrides `model_id`
- `api_base`: default API base
- `api_base_env_var`: optional env var name that overrides `api_base`
- `api_key_env_vars`: ordered list of env vars to try for the API key
- `requires_api_key`: whether Bastirr should fail early if no key resolves
- `request_kwargs`: extra kwargs forwarded to the underlying `smolagents` model constructor

For OpenRouter with the OpenAI SDK compatibility path, provider routing and reasoning controls belong under `request_kwargs.extra_body`.

### Anthropic (via LiteLLM)

```bash
# Via .env
BASTIRR_MODEL_BACKEND=litellm
BASTIRR_MODEL=anthropic/claude-3-5-sonnet-latest
BASTIRR_API_KEY=sk-ant-...

# Or via CLI
python3 -m bastirr.run_demo --backend litellm --model anthropic/claude-3-5-sonnet-latest
```

### Local Models (Ollama)

```bash
# Start Ollama server: ollama serve
# Pull model: ollama pull llama3.2

# Via .env
BASTIRR_MODEL_BACKEND=litellm
BASTIRR_MODEL=ollama_chat/llama3.2
BASTIRR_API_BASE=http://localhost:11434

# Or via CLI
python3 -m bastirr.run_demo \
  --backend litellm \
  --model ollama_chat/llama3.2 \
  --api-base http://localhost:11434
```

### Other Providers

LiteLLM supports 100+ providers. See [LiteLLM docs](https://docs.litellm.ai/) for provider-specific model IDs:

- **Azure OpenAI**: `azure/<DEPLOYMENT_NAME>`
- **AWS Bedrock**: `bedrock/anthropic.claude-3-sonnet-20240229-v1:0`
- **Google Vertex**: `vertex_ai/gemini-pro`
- **vLLM**: Set `BASTIRR_API_BASE` to your vLLM server URL

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

## CLI Arguments

```bash
python3 -m bastirr.run_demo [OPTIONS]

Options:
  --review-url URL     Cochrane review URL to process
  --split SPLIT        Dataset split: dev, val, random_test, heart_test, HIV_test
  --model MODEL_ID     Model identifier (e.g. gpt-5, anthropic/claude-3-5-sonnet-latest)
  --backend BACKEND    Model backend: openai (default) or litellm or hf-hub (local inference)
  --api-base URL       API base URL for local servers (e.g. http://localhost:11434)
  --model-profile KEY  Runtime model profile key from bastirr/runtime_config/model_profiles.json
  --list-reviews       List available reviews and exit
```

## Configuration Reference

All configuration lives in [`bastirr/config.py`](bastirr/config.py). Key settings:

| Setting | Source | Default | Description |
|---------|--------|---------|-------------|
| `BASTIRR_API_KEY` | `.env` | — | Preferred API key for OpenAI-compatible backends |
| `OPENAI_API_KEY` | `.env` | — | Legacy fallback for direct OpenAI if `BASTIRR_API_KEY` is unset |
| `BASTIRR_MODEL_BACKEND` | `.env` | `openai` | Model backend: `openai` or `litellm` |
| `BASTIRR_MODEL` | `.env` | `gpt-5` | Model identifier (provider-prefixed for LiteLLM) |
| `BASTIRR_API_BASE` | `.env` | — | API base URL for OpenAI-compatible or local servers |
| `BASTIRR_MODEL_PROFILE` | `.env` | — | Runtime model profile key |
| `BASTIRR_MODEL_PROFILES_CONFIG` | `.env` | `bastirr/runtime_config/model_profiles.json` | Alternate runtime model-profile file |
| `BASTIRR_EXECUTOR_TIMEOUT` | `.env` | `500` | Max seconds per code-execution step |
| `SEARCH_SOURCES` | `.env` | `local` | Comma-separated search sources: `local`, `bip`, `pubmed` |
| `SEARCH_BIP_MCP_URL` | `.env` | `https://bip-mcp.imsi.athenarc.gr/mcp` | BIP MCP endpoint (used when `bip` in `SEARCH_SOURCES`) |
| `SEARCH_BIP_AUTH_TOKEN` | `.env` | — | Bearer token for BIP MCP search endpoint (required for auth) |
| `SEARCH_PUBMED_MCP_URL` | `.env` | `https://pubmed-mcp.imsi.athenarc.gr/mcp` | PubMed MCP endpoint (used when `pubmed` in `SEARCH_SOURCES`) |
| `DATASET_DIR` | auto | `systematic_review_dataset/...` | Cochrane dataset directory |
