# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-04-09 02:08  
> **Duration:** 8m 16s  
> **Total tokens:** 526,160 (input: 474,220 / output: 51,940)

> **Benchmark suite:** screening_ladder  
> **Review key:** heart_failure_mhealth_200  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full  
> **Dataset split:** heart_test  
> **Studies:** 200  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI API]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI API]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 8m 16s | 7,370 / 5,162 |
| Gatekeeper | 5 | 7m 25s | 466,850 / 46,778 |
| **Total** | **7** | **8m 16s** | **474,220 / 51,940** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*02:09:33 — 34s — 6,582 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*02:17:16 — 7m 43s — 519,578 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
