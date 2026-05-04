# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-08 21:38  
> **Duration:** 4m 11s  
> **Total tokens:** 65,662 (input: 46,629 / output: 19,033)

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
| Orchestrator | 2 | 4m 11s | 8,243 / 6,038 |
| Gatekeeper | 1 | 2m 29s | 38,386 / 12,995 |
| **Total** | **3** | **4m 11s** | **46,629 / 19,033** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*21:39:38 — 54s — 7,199 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*21:42:55 — 3m 17s — 58,463 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
