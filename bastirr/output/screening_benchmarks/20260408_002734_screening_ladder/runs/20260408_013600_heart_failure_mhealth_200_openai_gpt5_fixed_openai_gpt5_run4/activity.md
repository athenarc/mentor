# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-04-08 01:36  
> **Duration:** 4m 31s  
> **Total tokens:** 283,393 (input: 260,735 / output: 22,658)

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
| Orchestrator | 2 | 4m 31s | 6,903 / 3,131 |
| Gatekeeper | 3 | 3m 54s | 253,832 / 19,527 |
| **Total** | **5** | **4m 31s** | **260,735 / 22,658** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:36:22 — 22s — 4,989 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:40:32 — 4m 09s — 278,404 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
