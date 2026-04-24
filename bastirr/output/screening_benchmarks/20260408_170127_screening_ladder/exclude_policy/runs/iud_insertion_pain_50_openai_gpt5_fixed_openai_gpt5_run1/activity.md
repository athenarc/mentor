# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-08 17:06  
> **Duration:** 3m 18s  
> **Total tokens:** 45,839 (input: 28,480 / output: 17,359)

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
| Orchestrator | 2 | 3m 18s | 6,846 / 8,050 |
| Gatekeeper | 1 | 1m 50s | 21,634 / 9,309 |
| **Total** | **3** | **3m 18s** | **28,480 / 17,359** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*17:06:49 — 48s — 7,546 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*17:09:19 — 2m 30s — 38,293 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
