# Bastirr — Multi-Agent Systematic Review Assistant

Scaffolding implementation of the Bastirr architecture using [smolagents](https://huggingface.co/docs/smolagents/).

## Architecture

```
                    ┌─────────────────┐
                    │   Orchestrator  │
                    │   (Manager)     │
                    └───────┬─────────┘
              ┌─────────────┼─────────────┐
              │             │             │
     ┌────────▼──┐  ┌───────▼───┐   ┌─────▼──────┐
     │ Librarian │  │ Gatekeeper│   │   Miner    │
     │ (Search)  │  │ (Screen)  │   │ (Extract)  │
     └───────────┘  └───────────┘   └─────┬──────┘
                                          │
                                   ┌──────▼──────┐
                                   │   Critic    │
                                   │ (Synthesize)│
                                   └─────────────┘
```

**Flow:** Orchestrator delegates to agents in sequence:
1. **Librarian** — retrieves candidate studies from the Cochrane dataset
2. **Gatekeeper** — screens each study (INCLUDE/EXCLUDE) against selection criteria
3. **Miner** — extracts PICO evidence from included studies' abstracts
4. **Critic** — assesses quality and synthesizes a citation-backed narrative

## Quick Start

```bash
# 1. Install dependencies
pip install -r bastirr/requirements.txt

# 2. Set up API key
#    Copy the template and add your OpenAI API key
cp .env.example .env
#    Then edit .env and set: OPENAI_API_KEY=sk-...

# 3. Ensure the dataset is downloaded
cd systematic_review_dataset && ./download_dataset.sh && cd ..

# 4. List available reviews
PYTHONPATH=. python3 -m bastirr.run_demo --list-reviews --split HIV_test

# 5. Run the demo (uses default HIV Cotrimoxazole review)
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
│   ├── search_tools.py      # Librarian's @tool functions
│   ├── screening_tools.py   # Gatekeeper's @tool functions
│   ├── extraction_tools.py  # Miner's @tool functions
│   └── synthesis_tools.py   # Critic's @tool functions
└── output/                  # Run outputs (report + logs, gitignored)
```

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `systematic_review_dataset/` | Provides the Cochrane dataset (8,608 reviews, 544K studies) used as the input source for Bastirr's demo. |
| `architecture_docs/` | Design specs that define the 5-agent architecture, MCP integration, and Expert-in-the-Loop approach that Bastirr implements. |

## Current Status: Scaffolding

This is a **scaffolding implementation** — the agents run end-to-end but with simplifications:

- **Librarian**: Returns pre-loaded studies from the dataset (no real PubMed/OpenAIRE search)
- **Gatekeeper**: Screens based on title/abstract only (no full-text retrieval)
- **Miner**: Extracts from abstracts only (no PDF OCR pipeline)
- **Critic**: Synthesizes from abstract-level evidence

### Next Steps

- [ ] Add real search via PubMed API (MCP server)
- [ ] Add full-text PDF retrieval and OCR (reuse `ocr_pdf_to_markdown.py`)
- [ ] Implement Expert-in-the-Loop checkpoints (smolagents `UserInputTool`)
- [ ] Add consistency checks and conflict resolution between agents
- [ ] Connect to the evaluation framework from `vaccine_indicators_demo`
- [ ] Persist pipeline state (MCP state server pattern)

## Demo Review

The default demo uses a small HIV review:
- **"Cotrimoxazole prophylaxis for opportunistic infections in children with HIV infection"**
- 10 studies total (1 included, 9 excluded at screening)
- From the HIV test set of the Cochrane dataset

## Configuration

All configuration in `bastirr/config.py`. Key settings:

| Setting | Source | Default |
|---------|--------|---------|
| `OPENAI_API_KEY` | `.env` | (required) |
| `BASTIRR_MODEL` | `.env` | `gpt-4o` |
| `DATASET_DIR` | auto | `systematic_review_dataset/20240827_Systematic_Review_Data/` |
