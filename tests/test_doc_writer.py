"""Tests for the doc writer (Stage 2)."""

from unittest.mock import Mock

from src.execution.doc_writer import DocWriter
from src.models.problem import ProblemContext, Difficulty


class TestDocWriter:
    def setup_method(self):
        self.mock_llm = Mock()
        self.mock_llm.generate.return_value = "Today I solved an interesting problem..."
        self.writer = DocWriter(self.mock_llm)

    def test_generate_doc_calls_llm(self):
        """Doc generation should call LLM with problem + code context."""
        problem = ProblemContext(
            title="Two Sum",
            difficulty=Difficulty.EASY,
            description="Find two numbers.",
            constraints="",
            source_url="https://leetcode.com/problems/two-sum/",
            language="cpp",
        )
        doc = self.writer.generate_doc(problem, "int main() {}")
        assert doc == "Today I solved an interesting problem..."
        self.mock_llm.generate.assert_called_once()

        # Verify system prompt is the doc writer prompt
        call_kwargs = self.mock_llm.generate.call_args[1]
        assert "journal" in call_kwargs["system_prompt"].lower()
        assert call_kwargs["temperature"] == 0.7

    def test_build_prompt_includes_code_and_problem(self):
        """The prompt should reference both problem and code."""
        problem = ProblemContext(
            title="Two Sum",
            difficulty=Difficulty.EASY,
            description="",
            constraints="",
            source_url="https://example.com",
            language="python",
        )
        prompt = self.writer._build_prompt(problem, "def solve(): pass")
        assert "Two Sum" in prompt
        assert "def solve()" in prompt
        assert "python" in prompt
