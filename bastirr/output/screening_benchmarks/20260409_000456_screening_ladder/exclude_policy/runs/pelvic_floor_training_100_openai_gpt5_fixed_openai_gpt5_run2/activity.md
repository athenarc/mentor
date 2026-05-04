# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-09 01:01  
> **Duration:** 3m 22s  
> **Total tokens:** 58,953 (input: 45,829 / output: 13,124)

> **Benchmark suite:** screening_ladder  
> **Review key:** pelvic_floor_training_100  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005654.pub4/full  
> **Dataset split:** random_test  
> **Studies:** 100  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 3m 22s | 7,338 / 4,976 |
| Gatekeeper | 1 | 1m 48s | 38,491 / 8,148 |
| **Total** | **3** | **3m 22s** | **45,829 / 13,124** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:02:25 — 42s — 6,592 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:05:05 — 2m 40s — 52,361 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
