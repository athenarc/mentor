# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-05-12 17:06  
> **Duration:** 47m 10s  
> **Total tokens:** 545,786 (input: 431,773 / output: 114,013)

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
| Orchestrator | 8 | 47m 09s | 46,336 / 3,632 |
| Gatekeeper | 18 | 45m 00s | 385,437 / 110,381 |
| **Total** | **26** | **47m 10s** | **431,773 / 114,013** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*17:06:09 — 9s — 3,581 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'candidates_data = json.loads(candidates_json)' due to: InterpreterError: The variable `json` is not defined.

---

### 2. Orchestrator (python_interpreter)

*17:06:15 — 6s — 3,661 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator → Gatekeeper

*17:32:21 — 26m 06s — 284,848 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator (python_interpreter)

*17:32:44 — 22s — 5,416 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'save_result = save_screening_evidence_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Incomplete screening response: expected 50 parsed decisions, found 0. Do not save partial

---

### 5. Orchestrator → Gatekeeper

*17:39:12 — 6m 28s — 123,548 tokens*

The orchestrator executed step 5. Used tools: python_interpreter.

---

### 6. Orchestrator → Gatekeeper

*17:52:49 — 13m 36s — 105,142 tokens*

The orchestrator executed step 6. Used tools: python_interpreter.

---

### 7. Orchestrator (python_interpreter)

*17:52:59 — 10s — 8,307 tokens*

The orchestrator executed step 7. Used tools: python_interpreter.

---

### 8. Final Output (Orchestrator)

*17:53:10 — 11s — 11,283 tokens*

The orchestrator executed step 8. Used tools: python_interpreter. Produced the final output.

---
