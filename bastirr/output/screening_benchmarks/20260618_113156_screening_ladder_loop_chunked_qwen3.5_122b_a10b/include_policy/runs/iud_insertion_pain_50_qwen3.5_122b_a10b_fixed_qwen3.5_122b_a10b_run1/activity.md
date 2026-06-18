# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-06-18 11:40  
> **Duration:** 6m 12s  
> **Total tokens:** 225,501 (input: 192,685 / output: 32,816)

> **Benchmark suite:** screening_ladder  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** iud_insertion_pain_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full  
> **Dataset split:** random_test  
> **Studies:** 50  
> **Chunk count:** 2  
> **Chunk sizes:** 25, 25  
> **Gatekeeper preset:** qwen3.5_122b_a10b  
> **Gatekeeper model:** qwen3.5-122b-a10b [Qwen 3.5 122B A10B]  
> **Orchestrator preset:** qwen3.5_122b_a10b  
> **Orchestrator model:** qwen3.5-122b-a10b [Qwen 3.5 122B A10B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 7 | 6m 12s | 32,570 / 2,866 |
| Gatekeeper | 6 | 5m 34s | 160,115 / 29,950 |
| **Total** | **13** | **6m 12s** | **192,685 / 32,816** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*11:40:35 — 7s — 4,286 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*11:44:35 — 3m 59s — 95,662 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*11:44:38 — 3s — 5,493 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*11:44:40 — 2s — 5,702 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 5. Orchestrator (python_interpreter)

*11:44:51 — 11s — 4,639 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 6. Orchestrator → Gatekeeper

*11:46:38 — 1m 46s — 104,302 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 7. Final Output (Orchestrator)

*11:46:41 — 4s — 5,417 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
