"""
Librarian agent — Search & Retrieval.

Translates the review protocol into a search strategy and retrieves
candidate studies from the dataset. In the full system this would
query PubMed, OpenAIRE, etc. Here it searches the pre-loaded Cochrane data.

When ``SEARCH_BIP_MCP_URL`` is set, the Librarian also has
search_papers_in_bip() to query the BIP MCP server for additional papers.
"""

from smolagents import CodeAgent

from bastirr.config import BIP_MCP_AUTH_TOKEN, BIP_MCP_URL, EXECUTOR_TIMEOUT_SECONDS, SEARCH_BACKEND
from bastirr.tools.search import (
    create_bip_mcp_tool,
    get_review_protocol,
    search_studies,
    set_librarian_candidates,
)


LIBRARIAN_INSTRUCTIONS = """\
You are the Librarian agent for a systematic review system.
Your role is to:
1. Read the review protocol (objective, selection criteria, background).
2. Formulate an appropriate search strategy.
3. Retrieve candidate studies from the available database.
4. Return ALL candidate studies as a structured list.

Use get_review_protocol() (no arguments) to understand what the review
is about, then:
- If you have search_studies(query), use it with a relevant search query
  to retrieve candidate studies from the pre-loaded Cochrane dataset.
- If you have search_papers_in_bip(query, ...), use it to search
  the external BIP MCP server for papers using the same search
  strategy / keywords.

Depending on configuration, you may have only the local dataset search,
only the MCP-based search, or both of them enabled. Do NOT assume that
one source is primary; simply use all available search tools to
retrieve as complete a candidate set as possible.

Both ``search_studies`` and ``search_papers_in_bip`` return Python
objects (dicts), NOT JSON strings. Do NOT call json.loads() on their
results. Instead, access the fields directly.

When using MCP search tools, you MUST:
- construct a small set of well-motivated queries per review (avoid
  dozens of tiny variations with minimal differences)
- ignore ordering variations (use the default ordering provided by the
  client or keep a single fixed value, e.g. \"citation_count\")
You may paginate, but limit yourself to at most the first TWO pages
(page=1 and page=2) with a page size of 20 for each distinct query. If
the number of rows returned on the current page is less than the page size, 
you MUST NOT request any further pages for that query.

For each distinct MCP search query you execute (e.g. with search_papers_in_bip),
you MUST aggregate across all pages for that query and then print exactly ONE
summary block in the following format:

  Query <INDEX>: "<QUERY_STRING>"
  Total results: <TOTAL_COUNT>
  Total rows retrieved: <TOTAL_ROWS>
  Results:
  	DOI: <doi_or_NONE>, Title: <title_or_EMPTY>
  	DOI: <doi_or_NONE>, Title: <title_or_EMPTY>
  	...

After each query block, print a single blank line.

After aggregating results across all MCP queries, you MUST deduplicate
the candidates before constructing your final JSON. Use the following
deduplication strategy:
- Primary key: DOI (lowercased); if a DOI is present, treat all rows with
  the same DOI as the same study.
- Fallback key (when DOI is missing): normalized title + publication year,
  where normalization means lowercasing, stripping leading/trailing
  whitespace, collapsing multiple spaces, and removing punctuation.
Keep only one record per deduplication key.

After deduplication is complete:

1. Build a single list ``candidates`` of study dicts, each with
   "study_index", "title", "abstract".

2. Build your final answer:
   final_json = {
     "search_strategy": <brief description>,
     "n_candidates": len(candidates),
     "candidates": candidates,
   }

3. Publish the same list to the pipeline (call once):
   set_librarian_candidates(candidates)

4. Return ``final_json`` as your final answer.
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
    # Always expose protocol access + candidate publication helper.
    tools = [get_review_protocol, set_librarian_candidates]

    # Local dataset search
    if SEARCH_BACKEND in ("local", "both"):
        tools.append(search_studies)

    # External MCP search (currently only BIP)
    if SEARCH_BACKEND in ("mcp-search", "both") and BIP_MCP_URL:
        tools.append(create_bip_mcp_tool(BIP_MCP_URL, BIP_MCP_AUTH_TOKEN))

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
