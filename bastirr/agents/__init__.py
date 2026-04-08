"""
Bastirr agents package — smolagents-based agents for systematic review.
"""

from bastirr.agents.librarian import create_librarian_agent
from bastirr.agents.gatekeeper import create_gatekeeper_agent
from bastirr.agents.miner import create_miner_agent
from bastirr.agents.critic import create_critic_agent
from bastirr.agents.orchestrator import create_orchestrator_agent
from bastirr.agents.screening_orchestrator import create_screening_orchestrator_agent

__all__ = [
    "create_librarian_agent",
    "create_gatekeeper_agent",
    "create_miner_agent",
    "create_critic_agent",
    "create_orchestrator_agent",
    "create_screening_orchestrator_agent",
]
