# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-08 00:37  
> **Duration:** 1m 30s  
> **Total tokens:** 19,213 (input: 12,357 / output: 6,856)

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
| Orchestrator | 2 | 1m 30s | 6,529 / 2,692 |
| Gatekeeper | 1 | 53s | 5,828 / 4,164 |
| **Total** | **3** | **1m 30s** | **12,357 / 6,856** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:37:25 — 22s — 4,539 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:38:34 — 1m 08s — 14,674 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
