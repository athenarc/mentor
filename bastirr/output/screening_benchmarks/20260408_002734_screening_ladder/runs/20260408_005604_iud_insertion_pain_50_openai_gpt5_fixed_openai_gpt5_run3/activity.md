# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-08 00:56  
> **Duration:** 2m 14s  
> **Total tokens:** 39,128 (input: 28,025 / output: 11,103)

> **Benchmark suite:** screening_ladder  
> **Review key:** iud_insertion_pain_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full  
> **Dataset split:** random_test  
> **Studies:** 50  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI API]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI API]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 14s | 6,731 / 3,051 |
| Gatekeeper | 1 | 1m 35s | 21,294 / 8,052 |
| **Total** | **3** | **2m 14s** | **28,025 / 11,103** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:56:28 — 24s — 4,863 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:58:18 — 1m 50s — 34,265 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
