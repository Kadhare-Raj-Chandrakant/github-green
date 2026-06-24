"""Tests for the code generator (Stage 1)."""

from unittest.mock import Mock, patch

from src.execution.code_generator import CodeGenerator
from src.models.problem import ProblemContext, Difficulty


class TestCodeGenerator:
    def setup_method(self):
        self.mock_llm = Mock()
        self.mock_llm.generate.return_value = "int main() { return 0; }"
        self.generator = CodeGenerator(self.mock_llm)

    def test_generate_code_calls_llm(self):
        """Code generation should call the LLM client with correct params."""
        problem = ProblemContext(
            title="Two Sum",
            difficulty=Difficulty.EASY,
            description="Find two numbers that add to target.",
            constraints="2 <= n <= 10^4",
            examples=[{"input": "[1,2,3], 5", "output": "[1,2]"}],
            boilerplate="class Solution {};",
            language="cpp",
        )
        code = self.generator.generate_code(problem)
        assert code == "int main() { return 0; }"
        self.mock_llm.generate.assert_called_once()

        # Verify system prompt is the code generator prompt
        call_kwargs = self.mock_llm.generate.call_args[1]
        assert "expert competitive programmer" in call_kwargs["system_prompt"].lower()
        assert call_kwargs["temperature"] == 0.2
        assert call_kwargs["max_tokens"] == 2048

    def test_clean_code_removes_fences(self):
        """Code with markdown fences should be cleaned."""
        dirty = "```cpp\nint main() {}\n```"
        clean = CodeGenerator._clean_code(dirty)
        assert clean == "int main() {}"

    def test_clean_code_preserves_clean(self):
        """Code without fences should be preserved."""
        code = "int main() { return 0; }"
        assert CodeGenerator._clean_code(code) == code

    def test_build_prompt_includes_problem_details(self):
        """The prompt should include title, difficulty, description, examples, constraints."""
        problem = ProblemContext(
            title="Two Sum",
            difficulty=Difficulty.MEDIUM,
            description="Find the two numbers.",
            constraints="2 <= n <= 10^4",
            examples=[{"input": "nums=[1,2], target=3", "output": "[0,1]"}],
            boilerplate="class Solution {};",
            language="cpp",
        )
        prompt = self.generator._build_prompt(problem)
        assert "Two Sum" in prompt
        assert "Medium" in prompt
        assert "Find the two numbers" in prompt
        assert "2 <= n <= 10^4" in prompt
        assert "class Solution {}" in prompt
