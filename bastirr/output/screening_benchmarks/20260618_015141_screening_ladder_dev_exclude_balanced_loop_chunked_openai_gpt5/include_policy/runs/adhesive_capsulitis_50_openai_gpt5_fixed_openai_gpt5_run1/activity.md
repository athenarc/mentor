# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-06-18 01:56  
> **Duration:** 6m 37s  
> **Total tokens:** 81,972 (input: 50,755 / output: 31,217)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Chunk count:** 2  
> **Chunk sizes:** 25, 25  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** openai-gpt-5 [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** openai-gpt-5 [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 3 | 3m 50s | 32,657 / 17,241 |
| Orchestrator | 4 | 6m 37s | 18,098 / 13,976 |
| **Total** | **7** | **6m 37s** | **50,755 / 31,217** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*01:58:47 — 1m 53s — 24,668 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---

### 2. Orchestrator (python_interpreter)

*01:59:57 — 1m 09s — 9,374 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 3. Orchestrator → Gatekeeper

*02:01:46 — 1m 49s — 22,335 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'append_result = append_screening_chunk_decisions_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_study_indices_json=chunk_indices_json_str,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Gatekeeper decisions m

---

### 4. Orchestrator → Gatekeeper

*02:03:31 — 1m 44s — 25,595 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
