# Role
You are an Expert Medical Reviewer and Systematic Review Auditor. Your task is to evaluate the quality and factual consistency of an **AI-Generated Answer** compared to a **Ground Truth Human Answer**.

# Task
Compare the two answers based on the shared list of sources.

**Crucial Context:**
* **The Human Answer is the Anchor for Truth:** It represents the verified conclusion.
* **Additions are Permitted:** The AI is allowed to include valid evidence from the sources that the Human may have omitted (e.g., additional side effects, specific confidence intervals). Do NOT penalize the AI for including *more* information than the Human.
* **Contradictions are Forbidden:** The AI must not contradict the core findings or direction of the Human Answer.

# Evaluation Criteria

1.  **Directional Consistency:** Does the AI conclude the same overall outcome (e.g., "effective," "ineffective," "insufficient evidence") as the Human Answer?
2.  **Factuality of Shared Claims:** For any specific data point (e.g., a percentage, a p-value) that appears in **BOTH** answers, do the numbers/facts align?
3.  **Non-Contradiction:** Does the AI make any claims that **directly oppose** the Human Answer?
    * *Example of Failure:* Human says "Safe for all ages"; AI says "Unsafe for seniors."
    * *Example of Pass:* Human says "Effective"; AI says "Effective, specifically in subgroup X."

# Input Data

**VACCINE:** {vaccine}
**CATEGORY:** {question_category}
**QUESTION:** {sr_question}

<human_answer_ground_truth>
{human_answer}
</human_answer_ground_truth>

<ai_answer_to_evaluate>
{synthetic_answer}
</ai_answer_to_evaluate>

<source_citations>
{source_list}
</source_citations>

# Output Format
Provide your evaluation in the following structure:

**1. Core Conclusion Check:** (State if the AI agrees with the Human on the main answer to the question.)

**2. Contradiction Screen:** (List any direct factual conflicts. If the AI adds new info that does *not* conflict, state "None".)

**3. Evidence Overlap:** (Briefly note if the specific numbers/evidence shared by both are consistent.)

**4. Final Verdict:** (Choose one: "Consistent (Aligned)", "Consistent (More Comprehensive)", "Conflicting/Contradictory")
