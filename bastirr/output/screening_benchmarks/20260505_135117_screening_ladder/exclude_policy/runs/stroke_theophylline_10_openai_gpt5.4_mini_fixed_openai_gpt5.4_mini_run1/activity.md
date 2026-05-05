# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-05-05 13:51  
> **Duration:** 43s  
> **Total tokens:** 67,728 (input: 62,420 / output: 5,308)

> **Benchmark suite:** screening_ladder  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Gatekeeper preset:** openai_gpt5.4_mini  
> **Gatekeeper model:** openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini]  
> **Orchestrator preset:** openai_gpt5.4_mini  
> **Orchestrator model:** openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 43s | 6,783 / 494 |
| Gatekeeper | 6 | 38s | 55,637 / 4,814 |
| **Total** | **8** | **43s** | **62,420 / 5,308** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*13:51:20 — 2s — 3,403 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*13:52:00 — 40s — 64,325 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
