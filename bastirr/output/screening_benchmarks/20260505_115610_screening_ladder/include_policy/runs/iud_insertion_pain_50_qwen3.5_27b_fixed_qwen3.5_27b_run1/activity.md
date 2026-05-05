# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-05-05 12:11  
> **Duration:** 4m 54s  
> **Total tokens:** 211,547 (input: 192,661 / output: 18,886)

> **Benchmark suite:** screening_ladder  
> **Review key:** iud_insertion_pain_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full  
> **Dataset split:** random_test  
> **Studies:** 50  
> **Gatekeeper preset:** qwen3.5_27b  
> **Gatekeeper model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator preset:** qwen3.5_27b  
> **Orchestrator model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 4m 54s | 27,033 / 1,215 |
| Gatekeeper | 4 | 4m 20s | 165,628 / 17,671 |
| **Total** | **8** | **4m 54s** | **192,661 / 18,886** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*12:11:32 — 7s — 3,820 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*12:16:01 — 4m 29s — 187,855 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*12:16:16 — 15s — 9,713 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*12:16:20 — 3s — 10,159 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
