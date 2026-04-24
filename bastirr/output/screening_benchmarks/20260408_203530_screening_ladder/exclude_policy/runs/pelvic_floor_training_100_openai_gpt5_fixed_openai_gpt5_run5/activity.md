# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-08 21:42  
> **Duration:** 6m 42s  
> **Total tokens:** 126,521 (input: 97,364 / output: 29,157)

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
| Orchestrator | 2 | 6m 41s | 7,327 / 6,948 |
| Gatekeeper | 2 | 4m 57s | 90,037 / 22,209 |
| **Total** | **4** | **6m 42s** | **97,364 / 29,157** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*21:44:11 — 1m 15s — 7,714 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*21:49:38 — 5m 26s — 118,807 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
