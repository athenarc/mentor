# Pipeline Activity Log

> **Review:** Factors that influence the provision of home‐based rehabilitation services for people needing rehabilitation: a qualitative evidence synthesis  
> **Date:** 2026-06-18 20:55  
> **Duration:** 21m 58s  
> **Total tokens:** 1,135,685 (input: 989,806 / output: 145,879)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** home_based_rehabilitation_183  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014823/full  
> **Dataset split:** dev  
> **Studies:** 183  
> **Chunk count:** 6  
> **Chunk sizes:** 31, 31, 31, 30, 30, 30  
> **Gatekeeper preset:** qwen3.5_122b_a10b  
> **Gatekeeper model:** qwen3.5-122b-a10b [Qwen 3.5 122B A10B]  
> **Orchestrator preset:** qwen3.5_122b_a10b  
> **Orchestrator model:** qwen3.5-122b-a10b [Qwen 3.5 122B A10B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 23 | 21m 57s | 114,764 / 9,941 |
| Gatekeeper | 20 | 20m 00s | 875,042 / 135,938 |
| **Total** | **43** | **21m 58s** | **989,806 / 145,879** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:55:04 — 3s — 4,139 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*20:58:44 — 3m 40s — 188,559 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*20:58:50 — 6s — 5,792 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*20:58:53 — 3s — 6,198 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 5. Orchestrator (python_interpreter)

*20:59:02 — 8s — 4,713 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 6. Orchestrator → Gatekeeper

*21:01:42 — 2m 40s — 80,698 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 7. Orchestrator (python_interpreter)

*21:01:45 — 3s — 5,417 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 8. Final Output (Orchestrator)

*21:01:48 — 2s — 5,611 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 9. Orchestrator → Gatekeeper

*21:03:22 — 1m 34s — 52,796 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---

### 10. Orchestrator (python_interpreter)

*21:03:30 — 8s — 4,321 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 11. Orchestrator → Gatekeeper

*21:05:06 — 1m 35s — 75,309 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 12. Orchestrator (python_interpreter)

*21:05:09 — 3s — 5,558 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 13. Final Output (Orchestrator)

*21:05:11 — 2s — 5,748 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 14. Orchestrator (python_interpreter)

*21:05:21 — 9s — 4,520 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 15. Orchestrator → Gatekeeper

*21:08:16 — 2m 55s — 119,455 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 16. Orchestrator (python_interpreter)

*21:08:19 — 2s — 5,325 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 17. Final Output (Orchestrator)

*21:08:20 — 2s — 5,540 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 18. Orchestrator (python_interpreter)

*21:08:25 — 5s — 4,332 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 19. Orchestrator → Gatekeeper

*21:11:07 — 2m 42s — 125,299 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 20. Orchestrator (python_interpreter)

*21:11:14 — 7s — 5,895 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'append_result = append_screening_chunk_decisions_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_study_indices_json=expected_study_indices_json,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Chunk response di

---

### 21. Orchestrator → Gatekeeper

*21:16:50 — 5m 35s — 404,659 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 22. Orchestrator (python_interpreter)

*21:16:56 — 6s — 7,570 tokens*

The orchestrator executed step 5. Used tools: python_interpreter.

---

### 23. Final Output (Orchestrator)

*21:16:59 — 3s — 8,231 tokens*

The orchestrator executed step 6. Used tools: python_interpreter. Produced the final output.

---
