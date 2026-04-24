# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-08 21:13  
> **Duration:** 3m 10s  
> **Total tokens:** 41,366 (input: 28,811 / output: 12,555)

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
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 3m 10s | 7,308 / 5,614 |
| Gatekeeper | 1 | 1m 55s | 21,503 / 6,941 |
| **Total** | **3** | **3m 10s** | **28,811 / 12,555** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*21:14:22 — 45s — 6,761 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*21:16:48 — 2m 25s — 34,605 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
