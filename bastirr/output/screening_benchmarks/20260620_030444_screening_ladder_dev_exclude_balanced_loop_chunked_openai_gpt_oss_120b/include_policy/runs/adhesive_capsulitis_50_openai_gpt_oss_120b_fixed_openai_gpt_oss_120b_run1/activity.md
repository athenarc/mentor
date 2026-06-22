# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-06-20 03:09  
> **Duration:** 14m 14s  
> **Total tokens:** 1,169,809 (input: 1,115,211 / output: 54,598)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Chunk count:** 2  
> **Chunk sizes:** 25, 25  
> **Gatekeeper preset:** openai_gpt_oss_120b  
> **Gatekeeper model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator preset:** openai_gpt_oss_120b  
> **Orchestrator model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator policy:** fixed  
> **Orchestrator max steps:** 30  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 12 | 14m 14s | 57,675 / 9,240 |
| Gatekeeper | 64 | 11m 47s | 1,057,536 / 45,358 |
| **Total** | **76** | **14m 14s** | **1,115,211 / 54,598** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*03:09:33 — 12s — 4,246 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*03:11:02 — 1m 29s — 50,562 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*03:11:09 — 7s — 4,716 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'append_result = append_screening_chunk_decisions_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_study_indices_json=expected_study_indices_json,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Gatekeeper decisi

---

### 4. Orchestrator → Gatekeeper

*03:12:28 — 1m 18s — 57,167 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 5. Orchestrator (python_interpreter)

*03:12:31 — 3s — 5,763 tokens*

The orchestrator executed step 5. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'append_result = append_screening_chunk_decisions_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_study_indices_json=expected_study_indices_json,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Chunk response di

---

### 6. Orchestrator (python_interpreter)

*03:12:57 — 26s — 7,458 tokens*

The orchestrator executed step 6. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code parsing failed on line 32 due to: SyntaxError: unexpected character after line continuation character (<unknown>, line 32)
gatekeeper_task = textwrap.dedent(f\"\"\"
                                     ^

---

### 7. Orchestrator → Gatekeeper

*03:14:36 — 1m 38s — 86,367 tokens*

The orchestrator executed step 7. Used tools: python_interpreter. Produced the final output.

---

### 8. Orchestrator — Step 1

*03:14:43 — 8s — 4,031 tokens*

The orchestrator executed step 1. Encountered an error.

> ⚠️ **Error:** Error in code parsing:
expected string or bytes-like object, got 'NoneType'
Make sure to provide correct code blobs.

---

### 9. Orchestrator → Gatekeeper

*03:16:42 — 1m 58s — 63,340 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---

### 10. Orchestrator → Gatekeeper

*03:18:55 — 2m 13s — 384,420 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'append_screening_chunk_decisions_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_study_indices_json=study_indices_json,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Chunk response did not match expected stud

---

### 11. Orchestrator → Gatekeeper

*03:21:17 — 2m 21s — 377,880 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'append_screening_chunk_decisions_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_study_indices_json=study_indices_json,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Chunk response did not match expected stud

---

### 12. Orchestrator → Gatekeeper

*03:23:35 — 2m 18s — 123,859 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
