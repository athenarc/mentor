# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-05-28 00:05  
> **Duration:** 32m 14s  
> **Total tokens:** 579,352 (input: 528,572 / output: 50,780)

> **Benchmark suite:** screening_ladder  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Gatekeeper preset:** nvidia_nemotron_3_super_120b_a12b  
> **Gatekeeper model:** nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B]  
> **Orchestrator preset:** nvidia_nemotron_3_super_120b_a12b  
> **Orchestrator model:** nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 18 | 32m 14s | 200,876 / 15,732 |
| Gatekeeper | 22 | 22m 23s | 327,696 / 35,048 |
| **Total** | **40** | **32m 14s** | **528,572 / 50,780** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:08:53 — 3m 19s — 8,307 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:16:12 — 7m 19s — 135,089 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*00:16:19 — 6s — 4,014 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator (python_interpreter)

*00:16:30 — 12s — 5,223 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'save_screening_evidence_json(
    screening_response=gatekeeper_response,
    output_dir="/var/folders/b7/kwcv3jkx39912qqb079d7xym0000gn/T/screening_benchmark_raw_w9p5d3_r/20260528_000533_stroke_theophylline_10_nvidia_nemotron_3_super_120b_a12b_fix",
    expected_n_stu

---

### 5. Orchestrator (python_interpreter)

*00:17:03 — 32s — 6,265 tokens*

The orchestrator executed step 5. Used tools: python_interpreter.

---

### 6. Orchestrator (python_interpreter)

*00:17:59 — 56s — 10,112 tokens*

The orchestrator executed step 6. Used tools: python_interpreter.

---

### 7. Orchestrator (python_interpreter)

*00:19:28 — 1m 29s — 11,464 tokens*

The orchestrator executed step 7. Used tools: python_interpreter.

---

### 8. Orchestrator → Gatekeeper

*00:27:36 — 8m 08s — 197,294 tokens*

The orchestrator executed step 8. Used tools: python_interpreter.

---

### 9. Orchestrator (python_interpreter)

*00:27:40 — 3s — 9,617 tokens*

The orchestrator executed step 9. Used tools: python_interpreter.

---

### 10. Orchestrator (python_interpreter)

*00:27:57 — 18s — 13,058 tokens*

The orchestrator executed step 10. Used tools: python_interpreter.

---

### 11. Orchestrator → Gatekeeper

*00:34:07 — 6m 09s — 49,536 tokens*

The orchestrator executed step 11. Used tools: python_interpreter.

---

### 12. Orchestrator (python_interpreter)

*00:34:13 — 6s — 13,829 tokens*

The orchestrator executed step 12. Used tools: python_interpreter.

---

### 13. Orchestrator (python_interpreter)

*00:34:31 — 18s — 15,311 tokens*

The orchestrator executed step 13. Used tools: python_interpreter.

---

### 14. Orchestrator → Gatekeeper

*00:37:09 — 2m 38s — 26,516 tokens*

The orchestrator executed step 14. Used tools: python_interpreter.

---

### 15. Orchestrator (python_interpreter)

*00:37:22 — 13s — 17,048 tokens*

The orchestrator executed step 15. Used tools: python_interpreter.

---

### 16. Orchestrator (python_interpreter)

*00:37:40 — 18s — 18,838 tokens*

The orchestrator executed step 16. Used tools: python_interpreter.

---

### 17. Orchestrator (python_interpreter)

*00:37:44 — 4s — 18,823 tokens*

The orchestrator executed step 17. Used tools: python_interpreter.

---

### 18. Final Output (Orchestrator)

*00:37:47 — 3s — 19,008 tokens*

The orchestrator executed step 18. Used tools: python_interpreter. Produced the final output.

---
