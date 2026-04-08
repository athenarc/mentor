# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-08 00:29  
> **Duration:** 3m 08s  
> **Total tokens:** 35,132 (input: 21,157 / output: 13,975)

> **Benchmark suite:** screening_ladder  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI API]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI API]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 3m 08s | 6,598 / 3,522 |
| Gatekeeper | 2 | 2m 10s | 14,559 / 10,453 |
| **Total** | **4** | **3m 08s** | **21,157 / 13,975** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:30:00 — 27s — 4,784 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:32:43 — 2m 42s — 30,348 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
