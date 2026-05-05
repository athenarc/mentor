# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-05-05 13:06  
> **Duration:** 21s  
> **Total tokens:** 30,414 (input: 27,786 / output: 2,628)

> **Benchmark suite:** screening_ladder  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Gatekeeper preset:** mistral_medium_3.5  
> **Gatekeeper model:** mistral-medium-3.5 [Mistral Medium 3.5]  
> **Orchestrator preset:** mistral_medium_3.5  
> **Orchestrator model:** mistral-medium-3.5 [Mistral Medium 3.5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 3 | 21s | 12,475 / 556 |
| Gatekeeper | 2 | 14s | 15,311 / 2,072 |
| **Total** | **5** | **21s** | **27,786 / 2,628** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*13:06:35 — 2s — 3,649 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*13:06:51 — 16s — 21,448 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*13:06:54 — 3s — 5,317 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
