# Pipeline Activity Log

> **Review:** Effects of glucocorticoids on radiological progression in rheumatoid arthritis  
> **Date:** 2026-05-27 20:19  
> **Duration:** 17m 25s  
> **Total tokens:** 77,143 (input: 52,708 / output: 24,435)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5_v2  
> **Review key:** glucocorticoids_rheumatoid_26  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD006356/full  
> **Dataset split:** dev  
> **Studies:** 26  
> **Gatekeeper preset:** openai_gpt5--xhigh  
> **Gatekeeper model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5--xhigh  
> **Orchestrator model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 17m 25s | 7,431 / 10,154 |
| Gatekeeper | 2 | 11m 32s | 45,277 / 14,281 |
| **Total** | **4** | **17m 25s** | **52,708 / 24,435** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:23:26 — 3m 37s — 9,666 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*20:37:14 — 13m 48s — 67,477 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
