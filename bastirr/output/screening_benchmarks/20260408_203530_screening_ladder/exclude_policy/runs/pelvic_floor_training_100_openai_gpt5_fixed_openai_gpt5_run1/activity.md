# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-08 21:25  
> **Duration:** 5m 38s  
> **Total tokens:** 64,062 (input: 46,342 / output: 17,720)

> **Benchmark suite:** screening_ladder  
> **Review key:** pelvic_floor_training_100  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005654.pub4/full  
> **Dataset split:** random_test  
> **Studies:** 100  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI API]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI API]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 5m 38s | 7,921 / 6,656 |
| Gatekeeper | 1 | 3m 35s | 38,421 / 11,064 |
| **Total** | **3** | **5m 38s** | **46,342 / 17,720** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*21:26:19 — 1m 01s — 7,772 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*21:30:55 — 4m 36s — 56,290 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
