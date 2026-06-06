# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-05-14 11:31  
> **Duration:** 2m 40s  
> **Total tokens:** 67,326 (input: 45,702 / output: 21,624)

> **Benchmark suite:** screening_ladder  
> **Review key:** pelvic_floor_training_100  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005654.pub4/full  
> **Dataset split:** random_test  
> **Studies:** 100  
> **Gatekeeper preset:** openai_gpt5--xhigh  
> **Gatekeeper model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5--xhigh  
> **Orchestrator model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 40s | 7,219 / 7,017 |
| Gatekeeper | 1 | 1m 44s | 38,483 / 14,607 |
| **Total** | **3** | **2m 40s** | **45,702 / 21,624** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*11:31:41 — 35s — 7,707 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*11:33:47 — 2m 05s — 59,619 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
