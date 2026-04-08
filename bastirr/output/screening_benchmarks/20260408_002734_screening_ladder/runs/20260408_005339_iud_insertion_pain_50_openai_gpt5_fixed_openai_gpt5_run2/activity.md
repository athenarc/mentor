# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-08 00:53  
> **Duration:** 2m 24s  
> **Total tokens:** 40,382 (input: 28,019 / output: 12,363)

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
| Orchestrator | 2 | 2m 24s | 6,626 / 3,658 |
| Gatekeeper | 1 | 1m 43s | 21,393 / 8,705 |
| **Total** | **3** | **2m 24s** | **28,019 / 12,363** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:54:04 — 25s — 5,416 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:56:04 — 1m 59s — 34,966 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
