# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-04-09 00:57  
> **Duration:** 4m 18s  
> **Total tokens:** 60,631 (input: 45,849 / output: 14,782)

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
| Orchestrator | 2 | 4m 18s | 7,364 / 5,166 |
| Gatekeeper | 1 | 3m 04s | 38,485 / 9,616 |
| **Total** | **3** | **4m 18s** | **45,849 / 14,782** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:58:06 — 42s — 6,201 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:01:42 — 3m 36s — 54,430 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
