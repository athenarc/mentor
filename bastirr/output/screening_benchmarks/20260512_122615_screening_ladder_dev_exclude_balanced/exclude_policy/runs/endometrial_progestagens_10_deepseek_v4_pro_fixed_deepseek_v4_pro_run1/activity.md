# Pipeline Activity Log

> **Review:** Adjuvant progestagens for endometrial cancer  
> **Date:** 2026-05-12 12:26  
> **Duration:** 3m 39s  
> **Total tokens:** 23,150 (input: 16,624 / output: 6,526)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** endometrial_progestagens_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full  
> **Dataset split:** dev  
> **Studies:** 10  
> **Gatekeeper preset:** deepseek_v4_pro  
> **Gatekeeper model:** deepseek-v4-pro [DeepSeek V4 Pro]  
> **Orchestrator preset:** deepseek_v4_pro  
> **Orchestrator model:** deepseek-v4-pro [DeepSeek V4 Pro]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 3 | 3m 39s | 11,729 / 2,587 |
| Gatekeeper | 1 | 2m 09s | 4,895 / 3,939 |
| **Total** | **4** | **3m 39s** | **16,624 / 6,526** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*12:27:13 — 51s — 4,746 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*12:29:54 — 2m 41s — 13,324 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*12:30:02 — 8s — 5,080 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
