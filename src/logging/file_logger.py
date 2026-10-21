"""Dual-write smolagents AgentLogger (terminal + workflow.log)."""

from __future__ import annotations

from typing import IO

from rich.console import Console
from smolagents.monitoring import AgentLogger, LogLevel


class FileAgentLogger(AgentLogger):
    """``AgentLogger`` subclass that mirrors *all* output to a log file.

    Every call to ``log()`` is rendered twice: to the terminal via the
    inherited Rich console, and to a plain-text log file via a second
    ``Console`` instance.
    """

    def __init__(self, level: LogLevel, log_file: IO[str]):
        super().__init__(level=level)
        self._log_file = log_file
        self._file_console = Console(
            file=self._log_file,
            highlight=True,
            force_terminal=False,
            no_color=False,
            width=120,
        )

    def log(self, *args, level: int | str | LogLevel = LogLevel.INFO, **kwargs):
        if isinstance(level, str):
            level = LogLevel[level.upper()]
        if level <= self.level:
            self.console.print(*args, **kwargs)
            self._file_console.print(*args, **kwargs)

    def visualize_agent_tree(self, agent):
        super().visualize_agent_tree(agent)
        self._render_agent_tree_to_file(agent)

    def _render_agent_tree_to_file(self, agent):
        from rich.tree import Tree

        def _build(parent, agent_obj):
            if agent_obj.tools:
                for name in agent_obj.tools:
                    parent.add(f"[tool] {name}")
            if agent_obj.managed_agents:
                for name, ma in agent_obj.managed_agents.items():
                    branch = parent.add(
                        f"{name} | {ma.__class__.__name__} | {ma.model.model_id}"
                    )
                    branch.add(f"description: {ma.description}")
                    _build(branch, ma)

        headline = f"{agent.__class__.__name__} | {agent.model.model_id}"
        tree = Tree(headline)
        _build(tree, agent)
        self._file_console.print(tree)

    def close(self):
        """Flush and close the log file."""
        self._log_file.flush()
        self._log_file.close()
