"""
Librarian agent — Search & Retrieval.

Translates the review protocol into a search strategy and retrieves
candidate studies from the dataset. In the full system this would
query PubMed, OpenAIRE, etc. Here it searches the pre-loaded Cochrane data.
"""

from smolagents import CodeAgent

from bastirr.config import EXECUTOR_TIMEOUT_SECONDS
from bastirr.tools.search_tools import search_studies, get_review_protocol


LIBRARIAN_INSTRUCTIONS = """\
You are the Librarian agent for a systematic review system.
Your role is to:
1. Read the review protocol (objective, selection criteria, background).
2. Formulate an appropriate search strategy.
3. Retrieve candidate studies from the available database.
4. Return ALL candidate studies as a structured list.

Use get_review_protocol() (no arguments) to understand what the review
is about, then use search_studies(query) with a relevant search query
to retrieve all candidate studies from the database.

Return your final answer as a JSON string with:
- "search_strategy": a brief description of how you'd search
- "n_candidates": number of studies found
- "candidates": list of objects with "study_index", "title", "abstract"
"""


def create_librarian_agent(model, step_callbacks=None, logger=None) -> CodeAgent:
    """
    Create the Librarian (Search & Retrieval) agent.

    Args:
        model: A smolagents model instance (e.g. OpenAIServerModel).
        step_callbacks: Optional callbacks invoked after each agent step.
        logger: Optional AgentLogger for dual-write logging.

    Returns:
        Configured CodeAgent for search and retrieval.
    """
    return CodeAgent(
        tools=[search_studies, get_review_protocol],
        model=model,
        name="librarian",
        description=(
            "Search and retrieval agent. Ask it to find candidate studies "
            "for the review and it searches the database, returning all "
            "candidates for screening."
        ),
        instructions=LIBRARIAN_INSTRUCTIONS,
        max_steps=5,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "typing", "yaml", "glob", "pandas", "numpy"],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )
