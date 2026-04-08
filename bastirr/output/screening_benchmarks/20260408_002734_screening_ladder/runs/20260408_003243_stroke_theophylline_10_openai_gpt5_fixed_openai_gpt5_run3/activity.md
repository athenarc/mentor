# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-08 00:32  
> **Duration:** 1m 56s  
> **Total tokens:** 21,388 (input: 12,448 / output: 8,940)

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
| Orchestrator | 2 | 1m 56s | 6,568 / 3,728 |
| Gatekeeper | 1 | 1m 06s | 5,880 / 5,212 |
| **Total** | **3** | **1m 56s** | **12,448 / 8,940** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:33:14 — 30s — 5,456 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:34:40 — 1m 26s — 15,932 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
