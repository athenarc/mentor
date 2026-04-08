# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-08 01:20  
> **Duration:** 3m 26s  
> **Total tokens:** 59,407 (input: 45,046 / output: 14,361)

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
| Orchestrator | 2 | 3m 26s | 6,671 / 3,694 |
| Gatekeeper | 1 | 2m 35s | 38,375 / 10,667 |
| **Total** | **3** | **3m 26s** | **45,046 / 14,361** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:21:29 — 32s — 5,395 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:24:23 — 2m 53s — 54,012 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
