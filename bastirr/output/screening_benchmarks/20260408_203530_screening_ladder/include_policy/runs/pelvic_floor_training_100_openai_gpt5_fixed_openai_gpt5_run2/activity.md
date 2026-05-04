# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-08 21:30  
> **Duration:** 3m 27s  
> **Total tokens:** 60,972 (input: 46,009 / output: 14,963)

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
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 3m 27s | 7,488 / 5,898 |
| Gatekeeper | 1 | 2m 01s | 38,521 / 9,065 |
| **Total** | **3** | **3m 27s** | **46,009 / 14,963** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*21:31:57 — 1m 01s — 7,551 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*21:34:23 — 2m 25s — 53,421 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
