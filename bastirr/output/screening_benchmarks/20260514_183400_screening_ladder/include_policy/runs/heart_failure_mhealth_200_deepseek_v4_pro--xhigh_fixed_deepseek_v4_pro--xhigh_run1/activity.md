# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-05-14 19:21  
> **Duration:** 14m 03s  
> **Total tokens:** 113,843 (input: 86,384 / output: 27,459)

> **Benchmark suite:** screening_ladder  
> **Review key:** heart_failure_mhealth_200  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full  
> **Dataset split:** heart_test  
> **Studies:** 200  
> **Gatekeeper preset:** deepseek_v4_pro--xhigh  
> **Gatekeeper model:** deepseek-v4-pro--xhigh [DeepSeek V4 Pro]  
> **Orchestrator preset:** deepseek_v4_pro--xhigh  
> **Orchestrator model:** deepseek-v4-pro--xhigh [DeepSeek V4 Pro]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 14m 03s | 7,651 / 4,689 |
| Gatekeeper | 1 | 11m 41s | 78,733 / 22,770 |
| **Total** | **3** | **14m 03s** | **86,384 / 27,459** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*19:23:01 — 1m 32s — 6,623 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*19:35:32 — 12m 30s — 107,220 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
