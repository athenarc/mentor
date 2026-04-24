# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-09 00:07  
> **Duration:** 2m 16s  
> **Total tokens:** 28,386 (input: 19,059 / output: 9,327)

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
| Orchestrator | 3 | 2m 16s | 13,004 / 5,784 |
| Gatekeeper | 1 | 43s | 6,055 / 3,543 |
| **Total** | **4** | **2m 16s** | **19,059 / 9,327** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:08:45 — 49s — 6,210 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:10:00 — 1m 14s — 15,465 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*00:10:12 — 13s — 6,711 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
