# Pipeline Activity Log

> **Review:** Factors that influence the provision of home‐based rehabilitation services for people needing rehabilitation: a qualitative evidence synthesis  
> **Date:** 2026-05-28 04:42  
> **Duration:** 19m 41s  
> **Total tokens:** 1,685,595 (input: 1,620,608 / output: 64,987)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Review key:** home_based_rehabilitation_183  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014823/full  
> **Dataset split:** dev  
> **Studies:** 183  
> **Gatekeeper preset:** nvidia_nemotron_3_super_120b_a12b  
> **Gatekeeper model:** nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B]  
> **Orchestrator preset:** nvidia_nemotron_3_super_120b_a12b  
> **Orchestrator model:** nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 10 | 19m 41s | 50,241 / 10,801 |
| Gatekeeper | 18 | 17m 38s | 1,570,367 / 54,186 |
| **Total** | **28** | **19m 41s** | **1,620,608 / 64,987** |

---

## Activity Timeline

### 1. Orchestrator — Step 1

*04:42:54 — 14s — 5,662 tokens*

The orchestrator executed step 1. Encountered an error.

> ⚠️ **Error:** Error in code parsing:
Your code snippet is invalid, because the regex pattern <code>(.*?)</code> was not found in it.
            Here is your code snippet:
            **Factors that influence the provision of home‐based rehabilitation services for people needing rehabilitation: a qualitative evid

---

### 2. Orchestrator (python_interpreter)

*04:43:00 — 7s — 5,646 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator → Gatekeeper

*04:53:26 — 10m 25s — 573,702 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator (python_interpreter)

*04:53:30 — 3s — 5,364 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 5. Orchestrator (python_interpreter)

*04:53:32 — 2s — 5,631 tokens*

The orchestrator executed step 5. Used tools: python_interpreter.

---

### 6. Final Output (Orchestrator)

*04:53:38 — 6s — 6,449 tokens*

The orchestrator executed step 6. Used tools: python_interpreter. Produced the final output.

---

### 7. Orchestrator (python_interpreter)

*04:53:56 — 18s — 6,617 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code parsing failed on line 9 due to: SyntaxError: unterminated string literal (detected at line 9) (<unknown>, line 9)
        "for the review titled 'Factors that influence the provision of home‐based rehabilitation services '         ^

---

### 8. Orchestrator → Gatekeeper

*04:55:46 — 1m 50s — 389,938 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'save_screening_evidence_json(
    screening_response=gatekeeper_response,
    output_dir="/var/folders/b7/kwcv3jkx39912qqb079d7xym0000gn/T/screening_benchmark_raw_nh_i2urm/20260528_044239_home_based_rehabilitation_183_nvidia_nemotron_3_super_120b_a",
    expected_n_stu

---

### 9. Orchestrator → Gatekeeper

*05:02:06 — 6m 20s — 678,326 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 10. Final Output (Orchestrator)

*05:02:21 — 15s — 8,260 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
