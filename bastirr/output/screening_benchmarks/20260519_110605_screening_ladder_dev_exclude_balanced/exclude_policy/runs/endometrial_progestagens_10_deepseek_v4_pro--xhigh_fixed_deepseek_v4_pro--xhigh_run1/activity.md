# Pipeline Activity Log

> **Review:** Adjuvant progestagens for endometrial cancer  
> **Date:** 2026-05-19 11:06  
> **Duration:** 5m 56s  
> **Total tokens:** 48,218 (input: 38,621 / output: 9,597)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** endometrial_progestagens_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full  
> **Dataset split:** dev  
> **Studies:** 10  
> **Gatekeeper preset:** deepseek_v4_pro--xhigh  
> **Gatekeeper model:** deepseek-v4-pro--xhigh [DeepSeek V4 Pro]  
> **Orchestrator preset:** deepseek_v4_pro--xhigh  
> **Orchestrator model:** deepseek-v4-pro--xhigh [DeepSeek V4 Pro]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 5m 55s | 9,022 / 1,091 |
| Gatekeeper | 3 | 5m 12s | 29,599 / 8,506 |
| **Total** | **5** | **5m 56s** | **38,621 / 9,597** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*11:06:33 — 18s — 3,781 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*11:12:11 — 5m 37s — 44,437 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
