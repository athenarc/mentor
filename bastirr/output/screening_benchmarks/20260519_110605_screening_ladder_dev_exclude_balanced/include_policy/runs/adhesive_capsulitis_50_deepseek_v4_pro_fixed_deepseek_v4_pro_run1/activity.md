# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-05-19 11:22  
> **Duration:** 9m 39s  
> **Total tokens:** 152,963 (input: 137,330 / output: 15,633)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Gatekeeper preset:** deepseek_v4_pro  
> **Gatekeeper model:** deepseek-v4-pro [DeepSeek V4 Pro]  
> **Orchestrator preset:** deepseek_v4_pro  
> **Orchestrator model:** deepseek-v4-pro [DeepSeek V4 Pro]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 9m 39s | 7,764 / 1,373 |
| Gatekeeper | 5 | 8m 49s | 129,566 / 14,260 |
| **Total** | **7** | **9m 39s** | **137,330 / 15,633** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*11:23:06 — 19s — 4,049 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*11:32:26 — 9m 19s — 148,914 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
