"""Tests for the repository structure manager."""

import tempfile
from pathlib import Path

from src.models.problem import ProblemContext, Difficulty
from src.repository.structure import StructureManager


class TestStructureManager:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.mgr = StructureManager(output_root=str(self.tmpdir / "LeetCode"))

    def test_write_solution_creates_file(self):
        """Writing a solution should create the file in the right folder."""
        problem = ProblemContext(
            title="Test Problem",
            difficulty=Difficulty.EASY,
            description="Desc",
            constraints="C",
            solved_date="2026-06-24",
            language="cpp",
        )
        path = self.mgr.write_solution(problem, "int main() {}")
        assert path.exists()
        assert path.suffix == ".cpp"
        assert "2026-06-24" in str(path)
        assert path.read_text() == "int main() {}"

    def test_write_readme_creates_file(self):
        """Writing a README should include the metadata header."""
        problem = ProblemContext(
            title="Two Sum",
            difficulty=Difficulty.MEDIUM,
            description="Desc",
            constraints="C",
            solved_date="2026-06-24",
            source="leetcode",
            source_url="https://leetcode.com/problems/two-sum/",
        )
        path = self.mgr.write_readme(problem, "My dev journal entry")
        assert path.exists()
        content = path.read_text()
        assert "# Two Sum" in content
        assert "**Difficulty**: Medium" in content
        assert "**Source**: [Leetcode]" in content
        assert "My dev journal entry" in content

    def test_language_extension_mapping(self):
        """Language names should map to correct file extensions."""
        assert StructureManager._language_extension("cpp") == ".cpp"
        assert StructureManager._language_extension("python") == ".py"
        assert StructureManager._language_extension("java") == ".java"
        assert StructureManager._language_extension("go") == ".go"
        assert StructureManager._language_extension("unknown") == ".unknown"
