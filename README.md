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

# 2. Set up API key
#    Copy the template and add your OpenAI API key
cp .env.example .env
#    Then edit .env and set: OPENAI_API_KEY=sk-...

# 3. Ensure the dataset is downloaded
cd systematic_review_dataset && ./download_dataset.sh && cd ..

# 4. List available reviews
PYTHONPATH=. python3 -m bastirr.run_demo --list-reviews --split HIV_test

# 5. Run the demo (uses default HIV Cotrimoxazole review with OpenAI)
PYTHONPATH=. python3 -m bastirr.run_demo
```

## Project Structure

```
bastirr/
├── __init__.py              # Package docstring
├── config.py                # Configuration, paths, API keys
├── logging_utils.py         # Run logging (workflow + decisions)
├── run_demo.py              # CLI entry point & end-to-end runner
├── requirements.txt         # Python dependencies
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
| `bastirr/` | Core agent package — agents, tools, config, data loader, CLI runner. |
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

### OpenAI (default)

Use OpenAI models like GPT-4o, GPT-4-turbo, GPT-5, etc.

```bash
# Via .env
BASTIRR_MODEL_BACKEND=openai
BASTIRR_MODEL=gpt-4o
OPENAI_API_KEY=sk-...

# Or via CLI
PYTHONPATH=. python3 -m bastirr.run_demo --model gpt-4o
```

### Anthropic (via LiteLLM)

```bash
# Via .env
BASTIRR_MODEL_BACKEND=litellm
BASTIRR_MODEL=anthropic/claude-3-5-sonnet-latest
BASTIRR_API_KEY=sk-ant-...

# Or via CLI
PYTHONPATH=. python3 -m bastirr.run_demo --backend litellm --model anthropic/claude-3-5-sonnet-latest
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
PYTHONPATH=. python3 -m bastirr.run_demo \
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

## CLI Arguments

```bash
PYTHONPATH=. python3 -m bastirr.run_demo [OPTIONS]

Options:
  --review-url URL     Cochrane review URL to process
  --split SPLIT        Dataset split: dev, val, random_test, heart_test, HIV_test
  --model MODEL_ID     Model identifier (e.g. gpt-4o, anthropic/claude-3-5-sonnet-latest)
  --backend BACKEND    Model backend: openai (default) or litellm
  --api-base URL       API base URL for local servers (e.g. http://localhost:11434)
  --list-reviews       List available reviews and exit
```

## Configuration Reference

All configuration lives in [`bastirr/config.py`](bastirr/config.py). Key settings:

| Setting | Source | Default | Description |
|---------|--------|---------|-------------|
| `OPENAI_API_KEY` | `.env` | (required for OpenAI) | OpenAI API key |
| `BASTIRR_MODEL_BACKEND` | `.env` | `openai` | Model backend: `openai` or `litellm` |
| `BASTIRR_MODEL` | `.env` | `gpt-4o` | Model identifier (provider-prefixed for LiteLLM) |
| `BASTIRR_API_BASE` | `.env` | — | API base URL for local servers |
| `BASTIRR_API_KEY` | `.env` | — | Generic API key for non-OpenAI providers |
| `BASTIRR_EXECUTOR_TIMEOUT` | `.env` | `500` | Max seconds per code-execution step |
| `DATASET_DIR` | auto | `systematic_review_dataset/...` | Cochrane dataset directory |
