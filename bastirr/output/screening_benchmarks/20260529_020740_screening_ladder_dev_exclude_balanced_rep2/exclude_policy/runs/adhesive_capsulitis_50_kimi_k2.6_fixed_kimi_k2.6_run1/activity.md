# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-05-29 02:51  
> **Duration:** 17m 29s  
> **Total tokens:** 140,746 (input: 96,389 / output: 44,357)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Gatekeeper preset:** kimi_k2.6  
> **Gatekeeper model:** kimi-k2.6 [Kimi K2.6]  
> **Orchestrator preset:** kimi_k2.6  
> **Orchestrator model:** kimi-k2.6 [Kimi K2.6]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 6 | 17m 29s | 29,158 / 2,673 |
| Gatekeeper | 3 | 16m 03s | 67,231 / 41,684 |
| **Total** | **9** | **17m 29s** | **96,389 / 44,357** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*02:51:30 — 10s — 3,664 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*03:07:53 — 16m 23s — 113,066 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*03:08:09 — 16s — 5,485 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator — Step 4

*03:08:23 — 14s — 5,972 tokens*

The orchestrator executed step 4. Encountered an error.

> ⚠️ **Error:** Error in code parsing:
expected string or bytes-like object, got 'NoneType'
Make sure to provide correct code blobs.

---

### 5. Orchestrator (python_interpreter)

*03:08:45 — 23s — 6,330 tokens*

The orchestrator executed step 5. Used tools: python_interpreter.

---

### 6. Final Output (Orchestrator)

*03:08:49 — 3s — 6,229 tokens*

The orchestrator executed step 6. Used tools: python_interpreter. Produced the final output.

---
