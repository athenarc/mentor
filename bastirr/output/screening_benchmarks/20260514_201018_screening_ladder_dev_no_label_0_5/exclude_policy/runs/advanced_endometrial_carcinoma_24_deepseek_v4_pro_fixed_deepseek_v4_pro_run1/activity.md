# Pipeline Activity Log

> **Review:** Chemotherapy for advanced, recurrent or metastatic endometrial carcinoma  
> **Date:** 2026-05-14 20:15  
> **Duration:** 4m 19s  
> **Total tokens:** 32,752 (input: 23,826 / output: 8,926)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Review key:** advanced_endometrial_carcinoma_24  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD003915.pub4/full  
> **Dataset split:** dev  
> **Studies:** 24  
> **Gatekeeper preset:** deepseek_v4_pro  
> **Gatekeeper model:** deepseek-v4-pro [DeepSeek V4 Pro]  
> **Orchestrator preset:** deepseek_v4_pro  
> **Orchestrator model:** deepseek-v4-pro [DeepSeek V4 Pro]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 3 | 4m 19s | 11,808 / 3,330 |
| Gatekeeper | 1 | 2m 36s | 12,018 / 5,596 |
| **Total** | **4** | **4m 19s** | **23,826 / 8,926** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:16:07 — 44s — 4,856 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*20:19:26 — 3m 19s — 22,862 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*20:19:42 — 16s — 5,034 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
