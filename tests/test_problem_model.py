"""Tests for the ProblemContext data model."""

from datetime import date
from src.models.problem import ProblemContext, Difficulty


class TestProblemContext:
    def test_folder_name_format(self):
        """Folder name should be YYYY-MM-DD-title-in-kebab-case."""
        problem = ProblemContext(
            title="Two Sum",
            difficulty=Difficulty.EASY,
            description="Description",
            constraints="Constraints",
            solved_date="2026-06-24",
            source="backlog",
        )
        folder = problem.folder_name()
        assert folder == "2026-06-24-two-sum"
        assert folder.count("-") >= 4  # date parts + kebab title

    def test_folder_name_special_chars(self):
        """Special characters in title should be stripped."""
        problem = ProblemContext(
            title="Valid Parentheses (Easy)",
            difficulty=Difficulty.EASY,
            description="",
            constraints="",
            solved_date="2026-06-24",
        )
        assert problem.folder_name() == "2026-06-24-valid-parentheses-easy"

    def test_commit_message_format(self):
        """Commit message should follow the pattern."""
        problem = ProblemContext(
            title="Reverse Linked List",
            difficulty=Difficulty.EASY,
            description="",
            constraints="",
            source="leetcode",
            solved_date="2026-06-24",
        )
        msg = problem.commit_message()
        assert "Leetcode" in msg
        assert "Reverse Linked List" in msg
        assert "2026-06-24" in msg

    def test_default_solved_date(self):
        """Default solved_date should be today."""
        problem = ProblemContext(
            title="Test",
            difficulty=Difficulty.MEDIUM,
            description="",
            constraints="",
        )
        assert problem.solved_date == date.today().isoformat()

    def test_from_backlog_entry(self):
        """Build ProblemContext from backlog dict."""
        entry = {
            "title": "Test Problem",
            "difficulty": "Hard",
            "description": "A hard problem",
            "constraints": "1 <= n <= 100",
            "examples": [{"input": "n=1", "output": "1"}],
            "boilerplate": "class Solution {};",
            "source_url": "https://leetcode.com/problems/test/",
        }
        problem = ProblemContext.from_backlog_entry(entry, language="cpp")
        assert problem.title == "Test Problem"
        assert problem.difficulty == Difficulty.HARD
        assert problem.language == "cpp"
        assert problem.source == "backlog"
        assert problem.boilerplate == "class Solution {};"
