# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-09 00:34  
> **Duration:** 2m 58s  
> **Total tokens:** 40,429 (input: 28,893 / output: 11,536)

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
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 58s | 7,279 / 5,750 |
| Gatekeeper | 1 | 1m 12s | 21,614 / 5,786 |
| **Total** | **3** | **2m 58s** | **28,893 / 11,536** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:35:12 — 52s — 6,668 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:37:18 — 2m 06s — 33,761 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
