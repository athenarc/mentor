"""
Librarian agent — Search & Retrieval.

Translates the review protocol into a search strategy and retrieves
candidate studies from the dataset. In the full system this would
query PubMed, OpenAIRE, etc. Here it searches the pre-loaded Cochrane data.

When ``SEARCH_BIP_MCP_URL`` is set, the Librarian also has
search_papers_in_bip() to query the BIP MCP server for additional papers.
"""

from smolagents import CodeAgent

from bastirr.config import (
    BIP_MCP_AUTH_TOKEN,
    BIP_MCP_URL,
    EXECUTOR_TIMEOUT_SECONDS,
)
from bastirr.mcp_clients import create_bip_mcp_tool
from bastirr.tools.search_tools import get_review_protocol, search_studies


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

If you have the search_papers_in_bip tool, you may also use it to search
the BIP MCP server for additional papers. Use the same search strategy
/ keywords. The primary candidate list for screening comes from
search_studies(); search_papers_in_bip is supplementary.

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
    tools = [search_studies, get_review_protocol]
    if BIP_MCP_URL:
        tools.append(
            create_bip_mcp_tool(BIP_MCP_URL, BIP_MCP_AUTH_TOKEN)
        )
    return CodeAgent(
        tools=tools,
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
