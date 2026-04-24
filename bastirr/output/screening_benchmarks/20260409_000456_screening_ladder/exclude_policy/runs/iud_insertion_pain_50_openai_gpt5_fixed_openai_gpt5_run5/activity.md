# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-09 00:50  
> **Duration:** 6m 35s  
> **Total tokens:** 89,963 (input: 61,267 / output: 28,696)

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
| Orchestrator | 2 | 6m 35s | 7,497 / 5,812 |
| Gatekeeper | 2 | 4m 44s | 53,770 / 22,884 |
| **Total** | **4** | **6m 35s** | **61,267 / 28,696** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:51:38 — 50s — 6,773 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:57:23 — 5m 44s — 83,190 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
