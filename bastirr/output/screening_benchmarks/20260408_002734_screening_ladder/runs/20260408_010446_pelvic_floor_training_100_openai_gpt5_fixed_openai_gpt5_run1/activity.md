# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-08 01:04  
> **Duration:** 2m 53s  
> **Total tokens:** 60,292 (input: 44,998 / output: 15,294)

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
| Orchestrator | 2 | 2m 53s | 6,713 / 3,315 |
| Gatekeeper | 1 | 2m 10s | 38,285 / 11,979 |
| **Total** | **3** | **2m 53s** | **44,998 / 15,294** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:05:06 — 20s — 4,826 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:07:39 — 2m 33s — 55,466 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
