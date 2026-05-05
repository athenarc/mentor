# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-05-05 13:54  
> **Duration:** 2m 37s  
> **Total tokens:** 244,875 (input: 217,665 / output: 27,210)

> **Benchmark suite:** screening_ladder  
> **Review key:** pelvic_floor_training_100  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005654.pub4/full  
> **Dataset split:** random_test  
> **Studies:** 100  
> **Gatekeeper preset:** openai_gpt5.4_mini  
> **Gatekeeper model:** openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini]  
> **Orchestrator preset:** openai_gpt5.4_mini  
> **Orchestrator model:** openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 37s | 7,100 / 507 |
| Gatekeeper | 4 | 2m 32s | 210,565 / 26,703 |
| **Total** | **6** | **2m 37s** | **217,665 / 27,210** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*13:54:44 — 3s — 3,572 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*13:57:19 — 2m 34s — 241,303 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
