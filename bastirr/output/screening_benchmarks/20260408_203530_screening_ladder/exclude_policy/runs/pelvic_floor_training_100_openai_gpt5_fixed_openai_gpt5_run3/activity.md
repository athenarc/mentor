# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-08 21:34  
> **Duration:** 4m 19s  
> **Total tokens:** 61,377 (input: 45,963 / output: 15,414)

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
| Orchestrator | 2 | 4m 19s | 7,403 / 6,046 |
| Gatekeeper | 1 | 2m 54s | 38,560 / 9,368 |
| **Total** | **3** | **4m 19s** | **45,963 / 15,414** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*21:35:14 — 50s — 7,105 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*21:38:43 — 3m 28s — 54,272 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
