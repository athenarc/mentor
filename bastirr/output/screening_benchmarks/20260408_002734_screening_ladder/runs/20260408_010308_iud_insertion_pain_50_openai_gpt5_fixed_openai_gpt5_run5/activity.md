# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-08 01:03  
> **Duration:** 1m 36s  
> **Total tokens:** 36,002 (input: 27,974 / output: 8,028)

> **Benchmark suite:** screening_ladder  
> **Review key:** iud_insertion_pain_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full  
> **Dataset split:** random_test  
> **Studies:** 50  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI API]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI API]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 1m 36s | 6,593 / 3,183 |
| Gatekeeper | 1 | 56s | 21,381 / 4,845 |
| **Total** | **3** | **1m 36s** | **27,974 / 8,028** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:03:30 — 22s — 4,959 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:04:45 — 1m 14s — 31,043 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
