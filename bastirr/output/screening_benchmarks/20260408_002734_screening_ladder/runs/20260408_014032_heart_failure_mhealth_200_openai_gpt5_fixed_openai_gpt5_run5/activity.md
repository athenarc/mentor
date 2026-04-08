# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-04-08 01:40  
> **Duration:** 4m 27s  
> **Total tokens:** 200,115 (input: 179,942 / output: 20,173)

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
| Orchestrator | 2 | 4m 27s | 6,964 / 3,363 |
| Gatekeeper | 2 | 3m 45s | 172,978 / 16,810 |
| **Total** | **4** | **4m 27s** | **179,942 / 20,173** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:40:55 — 22s — 5,184 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:45:00 — 4m 05s — 194,931 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
