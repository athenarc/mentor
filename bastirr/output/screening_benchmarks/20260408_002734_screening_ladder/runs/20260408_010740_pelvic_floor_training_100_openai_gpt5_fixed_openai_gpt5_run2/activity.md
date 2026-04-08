# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-08 01:07  
> **Duration:** 2m 08s  
> **Total tokens:** 57,878 (input: 44,969 / output: 12,909)

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
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 08s | 6,669 / 1,980 |
| Gatekeeper | 1 | 1m 44s | 38,300 / 10,929 |
| **Total** | **3** | **2m 08s** | **44,969 / 12,909** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:07:52 — 13s — 3,938 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:09:49 — 1m 56s — 53,940 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
