# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-09 01:05  
> **Duration:** 4m 27s  
> **Total tokens:** 64,299 (input: 46,032 / output: 18,267)

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
| Orchestrator | 2 | 4m 27s | 7,316 / 5,994 |
| Gatekeeper | 1 | 2m 56s | 38,716 / 12,273 |
| **Total** | **3** | **4m 27s** | **46,032 / 18,267** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:05:58 — 52s — 7,184 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:09:33 — 3m 35s — 57,115 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
