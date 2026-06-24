"""Tests for backlog ingestion."""

import json
from pathlib import Path
import tempfile

import pytest

from src.ingestion.backlog import BacklogFetcher
from src.ingestion.base import IngestionError


SAMPLE_BACKLOG = [
    {
        "title": "Sample Problem",
        "difficulty": "Easy",
        "description": "A test problem",
        "constraints": "1 <= n <= 10",
        "examples": [{"input": "n=5", "output": "5"}],
        "boilerplate": "class Solution {};",
        "source_url": "https://example.com/problem",
    }
]


class TestBacklogFetcher:
    def test_fetch_returns_problem_context(self):
        """Fetch should return a valid ProblemContext."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(SAMPLE_BACKLOG, f)
            backlog_path = f.name

        try:
            fetcher = BacklogFetcher(file_path=backlog_path)
            problem = fetcher.fetch()
            assert problem.title == "Sample Problem"
            assert problem.source == "backlog"
        finally:
            Path(backlog_path).unlink(missing_ok=True)

    def test_fetch_missing_file(self):
        """Missing backlog file should raise IngestionError."""
        fetcher = BacklogFetcher(file_path="/nonexistent/backlog.json")
        with pytest.raises(IngestionError, match="not found"):
            fetcher.fetch()

    def test_fetch_empty_backlog(self):
        """Empty backlog should raise IngestionError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([], f)
            backlog_path = f.name

        try:
            fetcher = BacklogFetcher(file_path=backlog_path)
            with pytest.raises(IngestionError, match="empty"):
                fetcher.fetch()
        finally:
            Path(backlog_path).unlink(missing_ok=True)

    def test_fetch_invalid_json(self):
        """Invalid JSON should raise IngestionError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json")
            backlog_path = f.name

        try:
            fetcher = BacklogFetcher(file_path=backlog_path)
            with pytest.raises(IngestionError, match="Failed to read"):
                fetcher.fetch()
        finally:
            Path(backlog_path).unlink(missing_ok=True)
