# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-04-08 23:14  
> **Duration:** 2m 45s  
> **Total tokens:** 99,554 (input: 86,843 / output: 12,711)

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
| Orchestrator | 2 | 2m 45s | 7,481 / 5,000 |
| Gatekeeper | 1 | 1m 44s | 79,362 / 7,711 |
| **Total** | **3** | **2m 45s** | **86,843 / 12,711** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*23:15:15 — 33s — 6,574 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*23:17:27 — 2m 12s — 92,980 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
