"""
Orchestrator agent — Manager & Coordinator.

The top-level agent that coordinates the end-to-end systematic review
workflow by delegating to specialised sub-agents (Librarian, Gatekeeper,
Miner, Critic) via smolagents' managed_agents pattern.
"""

from smolagents import CodeAgent

from bastirr.config import EXECUTOR_TIMEOUT_SECONDS
from bastirr.agents.librarian import create_librarian_agent
from bastirr.agents.gatekeeper import create_gatekeeper_agent
from bastirr.agents.miner import create_miner_agent
from bastirr.agents.critic import create_critic_agent
from bastirr.tools.report_tools import (
    format_report,
    save_evidence_json,
    extract_included_studies,
)


ORCHESTRATOR_INSTRUCTIONS = """\
You are the Orchestrator agent for the Bastirr Systematic Review system.
You coordinate a multi-agent pipeline to conduct a systematic review.

You have four managed agents:
1. **librarian** — retrieves candidate studies from the database
2. **gatekeeper** — screens studies for inclusion/exclusion
3. **miner** — extracts structured evidence from included studies
4. **critic** — assesses quality and synthesizes evidence

You also have three utility tools:
- **extract_included_studies** — parses the gatekeeper's response,
  filters to INCLUDE decisions, and returns the included studies as a
  JSON string ready for the miner.  ALWAYS use this instead of writing
  your own parsing code.
- **format_report** — takes the raw outputs from each agent and produces
  a clean, consistent Markdown report. ALWAYS use this as the last step.
- **save_evidence_json** — saves structured evidence as a separate JSON
  file alongside the report.

═══════════════════════════════════════════════════════════════════════
PLANNING GUIDANCE
═══════════════════════════════════════════════════════════════════════
During your planning/facts step, do NOT list or individually assess
each candidate study.  In large reviews there may be hundreds of
studies—enumerating them wastes tokens and biases later screening.
Instead, note only the review-level metadata (title, objective,
selection criteria, total candidate count) and proceed to Step 1.

═══════════════════════════════════════════════════════════════════════
CRITICAL RULES — read carefully before writing any code
═══════════════════════════════════════════════════════════════════════

1. ONE AGENT CALL PER CODE BLOCK.
   Sub-agent calls are slow. Putting two in one block will exceed the
   execution timeout. Write exactly ONE code block per workflow step.

2. ALWAYS USE YOUR TOOLS — NEVER WRITE YOUR OWN PARSERS.
   Your tools (extract_included_studies, format_report, save_evidence_json)
   handle all response parsing.  Do NOT write json.loads(), regex, or
   any other parsing code on agent responses.  If a tool exists for
   something, use it.  If you are unsure how to parse a response,
   pass it to the appropriate tool — that is what they are for.

3. VARIABLES PERSIST across code blocks.
   After each block finishes, every variable you defined is still
   available in the next block.  Reference them directly.  NEVER
   reconstruct or re-paste agent responses as string literals.

4. NEVER use locals(), globals(), exec(), or eval().

5. Keep code blocks SHORT — just the agent call, a tool call, and
   a print statement for progress.  No elaborate logic.

═══════════════════════════════════════════════════════════════════════

WORKFLOW — each step is ONE code block:

Code block 1 — SEARCH:
  review_data = json.loads(review_data_json)
  librarian_response = librarian(task=...)
  Print how many candidates were found.

Code block 2 — SCREENING:
  gatekeeper_response = gatekeeper(task=...)
  included_studies_json = extract_included_studies(
      screening_response=gatekeeper_response,
      review_data_json=review_data_json)
  Print how many studies were included.

  IMPORTANT — when drafting the gatekeeper task:
  • Provide the selection criteria verbatim.  Do NOT add phrases like
    "Be strict" or "only include" — the gatekeeper already has its own
    conservative guidelines and your override can cause false exclusions.
  • Do NOT pre-judge individual studies (e.g. "Study 1 should obviously
    be included").  The gatekeeper must make its own decisions.

Code block 3 — EXTRACTION:
  miner_response = miner(task=...)
  (pass included_studies_json from the previous block to the miner)

Code block 4 — SYNTHESIS:
  critic_response = critic(task=...)

Code block 5 — FORMAT & SAVE:
  report_str = format_report(
      review_title=..., review_objective=...,
      num_candidates=...,
      screening_response=gatekeeper_response,
      evidence_response=miner_response,
      synthesis_response=critic_response)
  save_evidence_json(
      evidence_response=miner_response,
      screening_response=gatekeeper_response,
      synthesis_response=critic_response,
      output_dir=output_dir)
  final_answer(report_str)

"""


def create_orchestrator_agent(model, step_callbacks=None, logger=None) -> CodeAgent:
    """
    Create the Orchestrator (Manager) agent with all sub-agents.

    This is the top-level agent that coordinates the full systematic
    review workflow. It delegates to the Librarian, Gatekeeper, Miner,
    and Critic agents using smolagents' managed_agents pattern.

    Args:
        model: A smolagents model instance (e.g. OpenAIServerModel).
        step_callbacks: Optional callbacks invoked after each agent step.
            Can be a list (registered for ActionStep only) or a dict
            mapping step types to callbacks (e.g.
            ``{ActionStep: fn, PlanningStep: fn}``).
        logger: Optional ``AgentLogger`` instance shared across all
            agents for dual-write logging (terminal + file).

    Returns:
        Configured CodeAgent that manages the full workflow.
    """
    # Create all sub-agents (share the same logger so all output is captured)
    librarian = create_librarian_agent(model, logger=logger)
    gatekeeper = create_gatekeeper_agent(model, logger=logger)
    miner = create_miner_agent(model, logger=logger)
    critic = create_critic_agent(model, logger=logger)

    return CodeAgent(
        tools=[format_report, save_evidence_json, extract_included_studies],
        model=model,
        managed_agents=[librarian, gatekeeper, miner, critic],
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        max_steps=10,
        planning_interval=3,  # Re-plan every 3 steps for complex workflows
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        step_callbacks=step_callbacks or [],
        additional_authorized_imports=["json", "re", "os"],
        logger=logger,
    )
