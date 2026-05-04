# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-09 01:09  
> **Duration:** 2m 55s  
> **Total tokens:** 60,487 (input: 46,288 / output: 14,199)

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
| Orchestrator | 2 | 2m 55s | 7,722 / 6,167 |
| Gatekeeper | 1 | 1m 22s | 38,566 / 8,032 |
| **Total** | **3** | **2m 55s** | **46,288 / 14,199** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:10:35 — 1m 00s — 7,332 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:12:29 — 1m 54s — 53,155 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
