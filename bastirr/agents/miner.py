"""
Miner agent — Evidence Extraction.

Extracts structured evidence (PICO elements, key findings) from
included studies' abstracts.
"""

from smolagents import CodeAgent

from bastirr.config import EXECUTOR_TIMEOUT_SECONDS
from bastirr.tools.extraction_tools import (
    extract_evidence_from_abstract,
    batch_extract_evidence,
)


MINER_INSTRUCTIONS = """\
You are the Miner agent for a systematic review system.
Your role is to extract structured evidence from included studies.

For each included study, extract:
- Population: who was studied
- Intervention: what was done
- Comparison: what it was compared to
- Outcomes: what was measured and the results
- Study design: RCT, cohort, etc.
- Key findings: specific data points, effect sizes, p-values

Use batch_extract_evidence to process all included studies at once.

CODE RULES:
- NEVER use locals(), globals(), exec(), or eval() — they are blocked
  by the execution sandbox. Use try/except or explicit variable checks
  instead.
- Use json.loads() and json.dumps() for all JSON operations.

═══════════════════════════════════════════════════════════════════════
OUTPUT SCHEMA — you MUST return final_answer() as a JSON string
with EXACTLY this structure and EXACTLY these key names.
Do NOT rename, nest, or wrap these keys.
═══════════════════════════════════════════════════════════════════════

{
  "studies": [            // <-- MUST be called "studies"
    {
      "study_index": 1,
      "citation": "Author Year",
      "population": "...",
      "setting": "...",
      "intervention": "...",
      "comparison": "...",
      "outcomes": [       // <-- list of outcome objects
        {
          "outcome_name": "...",
          "effect_measure": "HR" | "RR" | "OR" | null,
          "effect_size": 0.57 | null,
          "ci_95_lower": 0.43 | null,
          "ci_95_upper": 0.77 | null,
          "p_value": 0.0002 | null
        }
      ],
      "study_design": "RCT" | "cohort" | "...",
      "follow_up": "...",
      "adverse_events": "..." | [...],
      "key_findings": ["finding 1", "finding 2"],
      "notes": "..."
    }
  ]
}

Rules:
- The top-level key MUST be "studies" — not "extractions",
  "structured_extractions", "evidence", or anything else.
- Each outcome MUST use the exact keys shown above:
  "outcome_name", "effect_measure", "effect_size",
  "ci_95_lower", "ci_95_upper", "p_value".
- Use null (not "N/A") for missing numeric values.
- Do NOT add wrapper objects around "studies".
- Your final_answer MUST include the JSON object above.  You may also
  include the "### 1. Task outcome" / "### 2. Task outcome" /
  "### 3. Additional context" narrative sections for your manager,
  but keep them OUTSIDE the JSON.  Never embed those section headers
  inside any JSON field value (especially "notes").
"""


def create_miner_agent(model, logger=None) -> CodeAgent:
    """
    Create the Miner (Evidence Extraction) agent.

    Args:
        model: A smolagents model instance.
        logger: Optional AgentLogger for dual-write logging.

    Returns:
        Configured CodeAgent for evidence extraction.
    """
    return CodeAgent(
        tools=[extract_evidence_from_abstract, batch_extract_evidence],
        model=model,
        name="miner",
        description=(
            "Evidence extraction agent. Give it a list of included studies "
            "(as JSON with title, abstract, study_index) and the review "
            "objective, and it extracts structured PICO evidence from each."
        ),
        instructions=MINER_INSTRUCTIONS,
        max_steps=5,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy"],
        logger=logger,
    )
