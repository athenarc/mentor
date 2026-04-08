# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-08 00:58  
> **Duration:** 4m 49s  
> **Total tokens:** 141,779 (input: 108,955 / output: 32,824)

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
| Orchestrator | 2 | 4m 48s | 6,734 / 3,462 |
| Gatekeeper | 2 | 4m 13s | 102,221 / 29,362 |
| **Total** | **4** | **4m 49s** | **108,955 / 32,824** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:58:38 — 19s — 4,992 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:03:08 — 4m 29s — 136,787 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
