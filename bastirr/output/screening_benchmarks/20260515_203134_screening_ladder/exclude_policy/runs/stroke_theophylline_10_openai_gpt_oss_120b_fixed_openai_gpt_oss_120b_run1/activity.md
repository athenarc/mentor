# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-05-15 20:31  
> **Duration:** 3m 07s  
> **Total tokens:** 104,020 (input: 92,216 / output: 11,804)

> **Benchmark suite:** screening_ladder  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Gatekeeper preset:** openai_gpt_oss_120b  
> **Gatekeeper model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator preset:** openai_gpt_oss_120b  
> **Orchestrator model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 9 | 3m 06s | 50,300 / 5,433 |
| Gatekeeper | 6 | 1m 41s | 41,916 / 6,371 |
| **Total** | **15** | **3m 07s** | **92,216 / 11,804** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:31:42 — 7s — 3,878 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*20:32:49 — 1m 07s — 20,299 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'save_result = save_screening_evidence_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Incomplete screening response: expected 10 parsed decisions, found 0. Do not save partial

---

### 3. Orchestrator (python_interpreter)

*20:32:54 — 5s — 5,176 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator (python_interpreter)

*20:33:06 — 12s — 5,472 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 5. Orchestrator → Gatekeeper

*20:33:20 — 13s — 22,123 tokens*

The orchestrator executed step 5. Used tools: python_interpreter.

---

### 6. Orchestrator → Gatekeeper

*20:34:17 — 58s — 23,015 tokens*

The orchestrator executed step 6. Used tools: python_interpreter.

---

### 7. Orchestrator (python_interpreter)

*20:34:24 — 7s — 7,160 tokens*

The orchestrator executed step 7. Used tools: python_interpreter.

---

### 8. Orchestrator (python_interpreter)

*20:34:28 — 4s — 7,918 tokens*

The orchestrator executed step 8. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'save_result = save_screening_evidence_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Incomplete screening response: expected 10 parsed decisions, found 0. Do not save partial

---

### 9. Final Output (Orchestrator)

*20:34:42 — 13s — 8,979 tokens*

The orchestrator executed step 9. Used tools: python_interpreter. Produced the final output.

---
