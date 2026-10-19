"""
Librarian agent — search and candidate retrieval.

Exposes protocol helpers plus search tools selected by ``SEARCH_SOURCES`` in
``mentor.tools.search.settings``: local dataset search, BIP MCP, and/or PubMed MCP. The
librarian should publish the final candidate list with ``set_librarian_candidates``
so downstream getters and the gatekeeper see a consistent study store.
"""

from smolagents import CodeAgent

from mentor.settings import EXECUTOR_TIMEOUT_SECONDS
from mentor.tools.search.settings import (
    BIP_MCP_AUTH_TOKEN,
    BIP_MCP_URL,
    PUBMED_MCP_URL,
    SEARCH_SOURCES,
)
from mentor.agents.prompts import load_prompt
from mentor.tools.search import (
    create_bip_mcp_tool,
    create_pubmed_mcp_tool,
    get_review_protocol,
    search_studies,
    set_librarian_candidates,
)


def create_librarian_agent(
    model,
    step_callbacks=None,
    logger=None,
    instructions: str | None = None,
) -> CodeAgent:
    """
    Create the Librarian (Search & Retrieval) agent.

    Args:
        model: A smolagents model instance (e.g. OpenAIServerModel).
        step_callbacks: Optional callbacks invoked after each agent step.
        logger: Optional AgentLogger for dual-write logging.
        instructions: Optional system prompt override.

    Returns:
        Configured CodeAgent for search and retrieval.
    """
    # Always expose protocol access + candidate publication helper.
    tools = [get_review_protocol, set_librarian_candidates]

    # Local dataset search
    if "local" in SEARCH_SOURCES:
        tools.append(search_studies)

    # External MCP search: BIP
    if "bip" in SEARCH_SOURCES and BIP_MCP_URL:
        tools.append(create_bip_mcp_tool(BIP_MCP_URL, BIP_MCP_AUTH_TOKEN))

    # External MCP search: PubMed
    if "pubmed" in SEARCH_SOURCES and PUBMED_MCP_URL:
        tools.append(create_pubmed_mcp_tool(PUBMED_MCP_URL))

    return CodeAgent(
        tools=tools,
        model=model,
        name="librarian",
        description=(
            "Search and retrieval agent. Ask it to find candidate studies "
            "for the review and it searches the database, returning all "
            "candidates for screening."
        ),
        instructions=instructions or load_prompt("librarian"),
        max_steps=10,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "typing", "yaml", "glob", "pandas", "numpy"],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )
