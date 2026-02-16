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


ORCHESTRATOR_INSTRUCTIONS = """\
You are the Orchestrator agent for the Bastirr Systematic Review system.
You coordinate a multi-agent pipeline to conduct a systematic review.

You have four managed agents:
1. **librarian** — retrieves candidate studies from the database
2. **gatekeeper** — screens studies for inclusion/exclusion
3. **miner** — extracts structured evidence from included studies
4. **critic** — assesses quality and synthesizes evidence

WORKFLOW (execute these steps in order):

Step 1 - SEARCH: Call the librarian agent.
  Give it the review data JSON. Ask it to retrieve all candidate studies.
  It will return a JSON with candidate studies.

Step 2 - SCREENING: Call the gatekeeper agent.
  Give it the review data JSON. Ask it to screen each study and return
  INCLUDE/EXCLUDE decisions.
  Parse its response to identify which studies were included.

Step 3 - EXTRACTION: Call the miner agent.
  Give it the list of included studies (as JSON with title, abstract,
  study_index) and the review objective. Ask it to extract PICO evidence.

Step 4 - SYNTHESIS: Call the critic agent.
  Give it the extracted evidence JSON and the review objective.
  Ask it to assess quality and produce a narrative synthesis.

IMPORTANT:
- Pass data between agents as JSON strings.
- Each agent returns a string — parse it to extract the JSON results.
- After all steps complete, compile a final report.

Return your final answer as a structured report with sections:
1. Review Summary (title, objective)
2. Search Results (number of candidates found)
3. Screening Results (included/excluded counts, decisions)
4. Evidence Extraction Summary (key PICO elements per study)
5. Synthesis & Conclusions (the narrative synthesis)
6. Quality Assessment (evidence strength, limitations)
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
        tools=[],
        model=model,
        managed_agents=[librarian, gatekeeper, miner, critic],
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        max_steps=10,
        planning_interval=3,  # Re-plan every 3 steps for complex workflows
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        step_callbacks=step_callbacks or [],
        logger=logger,
    )
