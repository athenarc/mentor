"""
Mentor — multi-agent systematic review assistant.

Built on `smolagents` `CodeAgent` instances with role-specific prompts and
tools. The production entrypoint is `mentor.cli`; screening benchmarks live
under `experiments`.

Agent roles:

- **Librarian** — search and candidate retrieval (`mentor.tools.search`)
- **Gatekeeper** — title/abstract screening (`mentor.tools.screening_tools`)
- **Miner** — structured evidence extraction from abstracts
- **Critic** — synthesis and quality assessment
- **Orchestrator** — coordinates the full pipeline via `managed_agents`

Shared configuration is in `mentor.config`; run logging and session setup are
in `mentor.logging_utils` and `mentor.runtime.session`.
"""
