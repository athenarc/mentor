"""
Factory functions for Mentor ``CodeAgent`` roles.

Production pipeline: ``create_orchestrator_agent`` wires librarian, miner,
and critic as managed agents, with Gatekeeper screening via the
``screen_candidates`` tool (batched by ``batch_size``).
"""

from mentor.agents.librarian import create_librarian_agent
from mentor.agents.gatekeeper import create_gatekeeper_agent
from mentor.agents.miner import create_miner_agent
from mentor.agents.critic import create_critic_agent
from mentor.agents.orchestrator import create_orchestrator_agent

__all__ = [
    "create_librarian_agent",
    "create_gatekeeper_agent",
    "create_miner_agent",
    "create_critic_agent",
    "create_orchestrator_agent",
]
