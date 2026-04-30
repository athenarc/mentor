# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-28 01:03  
> **Duration:** 5m 54s  
> **Total tokens:** 96,973 (input: 83,179 / output: 13,794)

> **Benchmark suite:** screening_ladder  
> **Review key:** pelvic_floor_training_100  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005654.pub4/full  
> **Dataset split:** random_test  
> **Studies:** 100  
> **Gatekeeper preset:** deepseek_v4_pro  
> **Gatekeeper model:** deepseek-v4-pro [DeepSeek V4 Pro]  
> **Orchestrator preset:** deepseek_v4_pro  
> **Orchestrator model:** deepseek-v4-pro [DeepSeek V4 Pro]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 5m 54s | 7,064 / 859 |
| Gatekeeper | 2 | 5m 29s | 76,115 / 12,935 |
| **Total** | **4** | **5m 54s** | **83,179 / 13,794** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:04:12 — 13s — 3,761 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:09:53 — 5m 41s — 93,212 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
