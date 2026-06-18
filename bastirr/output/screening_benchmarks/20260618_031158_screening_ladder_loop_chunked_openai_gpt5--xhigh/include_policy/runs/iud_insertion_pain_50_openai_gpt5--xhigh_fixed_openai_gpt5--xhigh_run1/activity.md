# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-06-18 03:28  
> **Duration:** 9m 43s  
> **Total tokens:** 109,020 (input: 62,419 / output: 46,601)

> **Benchmark suite:** screening_ladder  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** iud_insertion_pain_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full  
> **Dataset split:** random_test  
> **Studies:** 50  
> **Chunk count:** 2  
> **Chunk sizes:** 25, 25  
> **Gatekeeper preset:** openai_gpt5--xhigh  
> **Gatekeeper model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5--xhigh  
> **Orchestrator model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 4 | 6m 56s | 55,603 / 32,651 |
| Orchestrator | 2 | 9m 43s | 6,816 / 13,950 |
| **Total** | **6** | **9m 43s** | **62,419 / 46,601** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*03:32:01 — 3m 11s — 33,724 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---

### 2. Orchestrator → Gatekeeper

*03:38:33 — 6m 31s — 75,296 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
