# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-08 20:39  
> **Duration:** 2m 53s  
> **Total tokens:** 48,426 (input: 31,946 / output: 16,480)

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
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 53s | 7,281 / 4,424 |
| Gatekeeper | 3 | 2m 10s | 24,665 / 12,056 |
| **Total** | **5** | **2m 53s** | **31,946 / 16,480** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:39:46 — 26s — 5,852 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*20:42:13 — 2m 27s — 42,574 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
