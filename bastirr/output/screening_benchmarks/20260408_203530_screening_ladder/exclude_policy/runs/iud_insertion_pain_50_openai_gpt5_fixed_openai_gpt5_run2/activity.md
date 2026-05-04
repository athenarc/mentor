# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-08 21:04  
> **Duration:** 6m 24s  
> **Total tokens:** 43,728 (input: 28,734 / output: 14,994)

> **Benchmark suite:** screening_ladder  
> **Review key:** iud_insertion_pain_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full  
> **Dataset split:** random_test  
> **Studies:** 50  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 6m 24s | 7,259 / 5,973 |
| Gatekeeper | 1 | 5m 08s | 21,475 / 9,021 |
| **Total** | **3** | **6m 24s** | **28,734 / 14,994** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*21:05:14 — 49s — 6,671 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*21:10:50 — 5m 35s — 37,057 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
