# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-09 00:40  
> **Duration:** 5m 11s  
> **Total tokens:** 45,888 (input: 29,551 / output: 16,337)

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
| Orchestrator | 2 | 5m 11s | 7,931 / 6,629 |
| Gatekeeper | 1 | 3m 31s | 21,620 / 9,708 |
| **Total** | **3** | **5m 11s** | **29,551 / 16,337** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:42:10 — 1m 13s — 7,849 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:46:08 — 3m 58s — 38,039 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
