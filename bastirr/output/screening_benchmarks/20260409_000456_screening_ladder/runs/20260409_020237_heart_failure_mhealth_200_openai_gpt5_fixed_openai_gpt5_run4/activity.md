# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-04-09 02:02  
> **Duration:** 6m 21s  
> **Total tokens:** 100,742 (input: 87,196 / output: 13,546)

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
| Orchestrator | 2 | 6m 21s | 7,649 / 5,377 |
| Gatekeeper | 1 | 5m 15s | 79,547 / 8,169 |
| **Total** | **3** | **6m 21s** | **87,196 / 13,546** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*02:03:13 — 35s — 5,890 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*02:08:59 — 5m 45s — 94,852 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
