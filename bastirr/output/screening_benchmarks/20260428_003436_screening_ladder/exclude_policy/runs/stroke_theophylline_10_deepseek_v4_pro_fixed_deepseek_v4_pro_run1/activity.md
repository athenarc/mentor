# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-28 00:34  
> **Duration:** 13m 09s  
> **Total tokens:** 22,543 (input: 18,207 / output: 4,336)

> **Benchmark suite:** screening_ladder  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
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
| Orchestrator | 3 | 13m 08s | 12,291 / 659 |
| Gatekeeper | 1 | 12m 46s | 5,916 / 3,677 |
| **Total** | **4** | **13m 09s** | **18,207 / 4,336** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:34:46 — 9s — 3,551 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:47:40 — 12m 53s — 13,577 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*00:47:46 — 6s — 5,415 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
