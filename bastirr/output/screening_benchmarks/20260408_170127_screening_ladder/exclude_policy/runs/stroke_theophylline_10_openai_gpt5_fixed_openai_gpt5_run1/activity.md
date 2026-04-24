# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-08 17:01  
> **Duration:** 1m 53s  
> **Total tokens:** 24,020 (input: 12,725 / output: 11,295)

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
| Orchestrator | 2 | 1m 53s | 6,658 / 6,805 |
| Gatekeeper | 1 | 39s | 6,067 / 4,490 |
| **Total** | **3** | **1m 53s** | **12,725 / 11,295** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*17:02:03 — 35s — 6,384 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*17:03:21 — 1m 17s — 17,636 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
