# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-08 01:14  
> **Duration:** 6m 49s  
> **Total tokens:** 208,539 (input: 168,789 / output: 39,750)

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
| Orchestrator | 2 | 6m 49s | 6,756 / 3,137 |
| Gatekeeper | 3 | 6m 09s | 162,033 / 36,613 |
| **Total** | **5** | **6m 49s** | **168,789 / 39,750** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:14:30 — 23s — 4,729 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:20:56 — 6m 26s — 203,810 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
