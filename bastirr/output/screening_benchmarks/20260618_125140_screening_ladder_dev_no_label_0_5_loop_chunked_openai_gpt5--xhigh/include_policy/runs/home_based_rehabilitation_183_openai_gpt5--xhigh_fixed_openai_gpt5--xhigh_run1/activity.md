# Pipeline Activity Log

> **Review:** Factors that influence the provision of home‐based rehabilitation services for people needing rehabilitation: a qualitative evidence synthesis  
> **Date:** 2026-06-18 13:37  
> **Duration:** 30m 06s  
> **Total tokens:** 387,006 (input: 228,367 / output: 158,639)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** home_based_rehabilitation_183  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014823/full  
> **Dataset split:** dev  
> **Studies:** 183  
> **Chunk count:** 6  
> **Chunk sizes:** 31, 31, 31, 30, 30, 30  
> **Gatekeeper preset:** openai_gpt5--xhigh  
> **Gatekeeper model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5--xhigh  
> **Orchestrator model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 12 | 30m 06s | 48,909 / 54,500 |
| Gatekeeper | 10 | 19m 01s | 179,458 / 104,139 |
| **Total** | **22** | **30m 06s** | **228,367 / 158,639** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*13:39:21 — 1m 30s — 9,394 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*13:41:48 — 2m 27s — 31,316 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---

### 3. Orchestrator (python_interpreter)

*13:43:01 — 1m 12s — 8,765 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 4. Orchestrator → Gatekeeper

*13:46:46 — 3m 45s — 64,301 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---

### 5. Orchestrator (python_interpreter)

*13:47:52 — 1m 06s — 9,920 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 6. Orchestrator (python_interpreter)

*13:48:26 — 34s — 7,551 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 7. Orchestrator → Gatekeeper

*13:50:27 — 2m 01s — 31,537 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---

### 8. Orchestrator → Gatekeeper

*13:54:48 — 4m 20s — 65,285 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---

### 9. Orchestrator (python_interpreter)

*13:55:48 — 1m 00s — 9,369 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 10. Orchestrator → Gatekeeper

*14:02:17 — 6m 29s — 76,353 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---

### 11. Orchestrator (python_interpreter)

*14:03:30 — 1m 12s — 8,151 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 12. Orchestrator → Gatekeeper

*14:07:56 — 4m 26s — 65,064 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
