# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-05-12 18:39  
> **Duration:** 5m 33s  
> **Total tokens:** 114,118 (input: 82,593 / output: 31,525)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
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
| Orchestrator | 2 | 5m 33s | 7,514 / 5,441 |
| Gatekeeper | 3 | 4m 29s | 75,079 / 26,084 |
| **Total** | **5** | **5m 33s** | **82,593 / 31,525** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*18:39:43 — 29s — 6,077 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*18:44:47 — 5m 03s — 108,041 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
