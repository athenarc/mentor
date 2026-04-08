# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-08 01:09  
> **Duration:** 4m 16s  
> **Total tokens:** 117,254 (input: 93,900 / output: 23,354)

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
| Orchestrator | 2 | 4m 16s | 6,666 / 2,959 |
| Gatekeeper | 2 | 3m 50s | 87,234 / 20,395 |
| **Total** | **4** | **4m 16s** | **93,900 / 23,354** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:10:06 — 17s — 4,987 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:14:06 — 3m 59s — 112,267 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
