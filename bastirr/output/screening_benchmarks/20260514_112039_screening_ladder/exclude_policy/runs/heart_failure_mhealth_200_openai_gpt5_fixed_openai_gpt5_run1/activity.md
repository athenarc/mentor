# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-05-14 11:33  
> **Duration:** 12m 32s  
> **Total tokens:** 458,373 (input: 358,990 / output: 99,383)

> **Benchmark suite:** screening_ladder  
> **Review key:** heart_failure_mhealth_200  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full  
> **Dataset split:** heart_test  
> **Studies:** 200  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 12m 32s | 7,470 / 10,579 |
| Gatekeeper | 4 | 11m 02s | 351,520 / 88,804 |
| **Total** | **6** | **12m 32s** | **358,990 / 99,383** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*11:34:32 — 45s — 8,130 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*11:46:19 — 11m 47s — 450,243 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
