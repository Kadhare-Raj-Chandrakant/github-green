"""Local backlog ingestion — the fail-safe fallback when LeetCode is unavailable."""

from __future__ import annotations

import json
import logging
import random
from pathlib import Path

from src.ingestion.base import ProblemFetcher, IngestionError
from src.models.problem import ProblemContext

log = logging.getLogger(__name__)


class BacklogFetcher(ProblemFetcher):
    """Fetches a random problem from the local backlog.json file.

    Activated when LeetCodeFetcher fails (network, rate-limit, API change).
    """

    def __init__(self, file_path: str | Path = "backlog.json", language: str = "cpp"):
        self.file_path = Path(file_path)
        self.language = language

    def fetch(self) -> ProblemContext:
        """Pick a random problem from the backlog."""
        log.info("Fetching problem from backlog: %s", self.file_path)
        if not self.file_path.exists():
            raise IngestionError(
                f"Backlog file not found: {self.file_path}. "
                "Create a backlog.json with at least one problem entry."
            )

        try:
            with open(self.file_path, "r") as f:
                entries = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise IngestionError(f"Failed to read backlog: {e}") from e

        if not entries:
            raise IngestionError("Backlog is empty — no problems available.")

        entry = random.choice(entries)
        log.info("Selected backlog problem: %s", entry["title"])
        return ProblemContext.from_backlog_entry(entry, language=self.language)
