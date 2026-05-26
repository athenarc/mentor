# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-05-22 19:23  
> **Duration:** 6m 44s  
> **Total tokens:** 494,114 (input: 457,474 / output: 36,640)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Gatekeeper preset:** qwen3.5_122b_a10b  
> **Gatekeeper model:** qwen3.5-122b-a10b [Qwen 3.5 122B A10B]  
> **Orchestrator preset:** qwen3.5_122b_a10b  
> **Orchestrator model:** qwen3.5-122b-a10b [Qwen 3.5 122B A10B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 5 | 6m 44s | 86,062 / 1,407 |
| Gatekeeper | 5 | 6m 16s | 371,412 / 35,233 |
| **Total** | **10** | **6m 44s** | **457,474 / 36,640** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*19:23:57 — 4s — 3,868 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'print(f"Candidates retrieved: {len(candidates_json.get('studies', []))} studies")' due to: InterpreterError: Object {"title": "Manual therapy and exercise for adhesive capsulitis (frozen shoulder)", "objective": "To synthesise available evidence regarding the benefits 

---

### 2. Orchestrator (python_interpreter)

*19:24:03 — 6s — 19,891 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator → Gatekeeper

*19:30:27 — 6m 24s — 427,116 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator (python_interpreter)

*19:30:34 — 7s — 21,398 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 5. Final Output (Orchestrator)

*19:30:37 — 3s — 21,841 tokens*

The orchestrator executed step 5. Used tools: python_interpreter. Produced the final output.

---
