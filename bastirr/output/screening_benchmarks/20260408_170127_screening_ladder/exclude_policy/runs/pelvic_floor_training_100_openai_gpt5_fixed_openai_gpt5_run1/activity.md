# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-08 17:09  
> **Duration:** 5m 44s  
> **Total tokens:** 219,133 (input: 188,579 / output: 30,554)

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
| Orchestrator | 2 | 5m 44s | 6,810 / 6,194 |
| Gatekeeper | 4 | 4m 36s | 181,769 / 24,360 |
| **Total** | **6** | **5m 44s** | **188,579 / 30,554** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*17:10:08 — 49s — 7,611 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*17:15:04 — 4m 55s — 211,522 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
