# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-04-08 01:29  
> **Duration:** 4m 04s  
> **Total tokens:** 290,031 (input: 273,288 / output: 16,743)

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
| Orchestrator | 2 | 4m 04s | 6,965 / 3,560 |
| Gatekeeper | 3 | 3m 08s | 266,323 / 13,183 |
| **Total** | **5** | **4m 04s** | **273,288 / 16,743** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:29:54 — 27s — 5,208 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:33:32 — 3m 37s — 284,823 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
