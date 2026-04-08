# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-04-08 01:24  
> **Duration:** 5m 03s  
> **Total tokens:** 299,241 (input: 275,478 / output: 23,763)

> **Benchmark suite:** screening_ladder  
> **Review key:** heart_failure_mhealth_200  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full  
> **Dataset split:** heart_test  
> **Studies:** 200  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI API]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI API]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 5m 03s | 6,885 / 3,563 |
| Gatekeeper | 3 | 4m 14s | 268,593 / 20,200 |
| **Total** | **5** | **5m 03s** | **275,478 / 23,763** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:24:48 — 24s — 5,101 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:29:27 — 4m 39s — 294,140 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
