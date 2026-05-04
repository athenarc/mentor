# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-08 20:44  
> **Duration:** 2m 31s  
> **Total tokens:** 39,138 (input: 22,599 / output: 16,539)

> **Benchmark suite:** screening_ladder  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 31s | 7,158 / 4,880 |
| Gatekeeper | 2 | 1m 47s | 15,441 / 11,659 |
| **Total** | **4** | **2m 31s** | **22,599 / 16,539** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:44:27 — 27s — 6,021 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*20:46:31 — 2m 04s — 33,117 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
