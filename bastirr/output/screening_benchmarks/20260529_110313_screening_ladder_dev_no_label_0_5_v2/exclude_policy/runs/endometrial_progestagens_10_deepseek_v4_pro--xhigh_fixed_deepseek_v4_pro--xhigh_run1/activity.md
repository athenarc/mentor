# Pipeline Activity Log

> **Review:** Adjuvant progestagens for endometrial cancer  
> **Date:** 2026-05-29 11:03  
> **Duration:** 2m 39s  
> **Total tokens:** 25,772 (input: 17,531 / output: 8,241)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5_v2  
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
| Orchestrator | 3 | 2m 39s | 12,417 / 4,105 |
| Gatekeeper | 1 | 1m 09s | 5,114 / 4,136 |
| **Total** | **4** | **2m 39s** | **17,531 / 8,241** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*11:04:31 — 1m 08s — 6,584 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*11:05:51 — 1m 19s — 13,430 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*11:06:03 — 11s — 5,758 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
