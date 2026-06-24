#!/usr/bin/env python3
"""GitHubGreenCard — Automated DSA Portfolio Engine.

Orchestrates the daily pipeline:
1. Ingest problem (LeetCode POTD → backlog fallback)
2. Generate solution code (LLM Stage 1)
3. Generate humanized docs (LLM Stage 2)
4. Write files to disk
5. Commit and push to GitHub
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import yaml

from src.ingestion.backlog import BacklogFetcher
from src.ingestion.leetcode import LeetCodeFetcher
from src.ingestion.base import IngestionError
from src.execution.code_generator import CodeGenerator
from src.execution.doc_writer import DocWriter
from src.execution.llm_client import LLMClient
from src.execution.exceptions import ExecutionError
from src.repository.structure import StructureManager
from src.repository.git_ops import GitManager

log = logging.getLogger("githubgreencard")


def load_config(path: str = "config.yaml") -> dict:
    """Load pipeline configuration from YAML file."""
    config_path = Path(path)
    if not config_path.exists():
        log.warning("Config file not found: %s — using defaults", path)
        return {}

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    log.info("Configuration loaded from: %s", path)
    return config or {}


def setup_logging(config: dict) -> None:
    """Configure logging based on config."""
    log_config = config.get("logging", {})
    level = getattr(logging, log_config.get("level", "INFO").upper(), logging.INFO)
    fmt = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    logging.basicConfig(
        level=level,
        format=fmt,
        stream=sys.stdout,
    )


def fetch_problem(config: dict) -> "ProblemContext":
    """Ingest a problem — try LeetCode first, fallback to backlog.

    Returns:
        ProblemContext from either source.

    Raises:
        IngestionError: If both sources fail.
    """
    ingestion_config = config.get("ingestion", {})
    language = config.get("pipeline", {}).get("language", "cpp")

    # Attempt primary: LeetCode
    leetcode_config = ingestion_config.get("leetcode", {})
    if leetcode_config.get("enabled", True):
        try:
            fetcher = LeetCodeFetcher(
                api_url=leetcode_config.get("api_url", "https://leetcode.com/graphql"),
                timeout=leetcode_config.get("timeout", 30),
                language=language,
            )
            problem = fetcher.fetch()
            log.info("Fetched LeetCode daily challenge: %s", problem.title)
            return problem
        except IngestionError as e:
            log.warning("LeetCode fetch failed: %s — switching to backlog", e)
    else:
        log.info("LeetCode ingestion disabled in config — using backlog")

    # Fallback: Backlog
    backlog_config = ingestion_config.get("backlog", {})
    backlog_path = backlog_config.get("file_path", "backlog.json")
    fetcher = BacklogFetcher(file_path=backlog_path, language=language)
    problem = fetcher.fetch()
    log.info("Fetched from backlog: %s", problem.title)
    return problem


def execute_pipeline(problem: "ProblemContext", config: dict) -> None:
    """Run the LLM execution pipeline on a problem.

    Args:
        problem: The problem to solve.
        config: Full pipeline config.
    """
    exec_config = config.get("execution", {}).get("llm", {})

    # Initialize LLM client (supports OpenAI + NVIDIA NIM + any OpenAI-compatible API)
    llm = LLMClient(
        base_url=exec_config.get("base_url"),
        model=exec_config.get("model", "nvidia/nemotron-mini-4b-instruct"),
        temperature=exec_config.get("temperature_code", 0.2),
        max_tokens=exec_config.get("max_tokens_code", 2048),
        retry_count=exec_config.get("retry_count", 3),
        retry_delay=exec_config.get("retry_delay", 5),
    )

    # Stage 1: Generate solution code
    code_gen = CodeGenerator(llm)
    solution_code = code_gen.generate_code(problem)
    log.info("Solution code generated (%d bytes)", len(solution_code))

    # Stage 2: Generate documentation
    doc_writer = DocWriter(llm)
    doc = doc_writer.generate_doc(problem, solution_code)
    log.info("Documentation generated (%d bytes)", len(doc))

    # Write to filesystem
    pipeline_config = config.get("pipeline", {})
    output_root = pipeline_config.get("output_root", "LeetCode")
    struct_mgr = StructureManager(output_root=output_root)
    solution_path = struct_mgr.write_solution(problem, solution_code)
    readme_path = struct_mgr.write_readme(problem, doc)

    log.info("Files written:")
    log.info("  Solution: %s", solution_path)
    log.info("  README:   %s", readme_path)


def deploy(problem: "ProblemContext", config: dict) -> bool:
    """Commit and push changes to GitHub.

    Args:
        problem: The problem that was solved.
        config: Pipeline config.

    Returns:
        True if commit+push succeeded.
    """
    repo_config = config.get("repository", {}).get("git", {})
    git_mgr = GitManager(
        branch=repo_config.get("branch", "main"),
        author_name=repo_config.get("author_name", "GitHubGreenCard Bot"),
        author_email=repo_config.get("author_email", "bot@githubgreencard.dev"),
    )

    # In GitHub Actions, set up git config
    if os.environ.get("GITHUB_ACTIONS") == "true":
        git_mgr.setup_git_config()

    return git_mgr.commit_and_push(problem)


def run_dry(config: dict) -> None:
    """Run the pipeline in dry-run mode — no git operations.

    Useful for testing the ingestion + LLM flow without pushing to GitHub.
    If no OPENAI_API_KEY is set, the LLM steps are skipped.
    """
    log.info("=== DRY RUN MODE ===")
    log.info("Step 1: Fetching problem...")
    problem = fetch_problem(config)
    log.info("  -> Title: %s", problem.title)
    log.info("  -> Difficulty: %s", problem.difficulty.value)
    log.info("  -> Source: %s", problem.source)

    log.info("Step 2-3: Executing LLM pipeline...")
    try:
        execute_pipeline(problem, config)
        log.info("Step 4: Skipping git operations (dry-run)")
        log.info("=== DRY RUN COMPLETE ===")
        log.info("Output directory: %s/%s", config.get("pipeline", {}).get("output_root", "LeetCode"), problem.folder_name())
    except ExecutionError as e:
        log.warning("LLM execution skipped: %s", e)
        log.warning("Set OPENAI_API_KEY to enable code generation.")
        log.info("=== DRY RUN PARTIAL (ingestion OK, LLM skipped) ===")


def run(config: dict) -> int:
    """Run the full production pipeline.

    Returns:
        0 on success, 1 on failure.
    """
    try:
        log.info("=" * 50)
        log.info("GitHubGreenCard Pipeline — Starting")
        log.info("=" * 50)

        problem = fetch_problem(config)
        execute_pipeline(problem, config)
        deployed = deploy(problem, config)

        if deployed:
            log.info("Pipeline complete — solution committed and pushed.")
        else:
            log.warning("Pipeline complete — nothing new to commit.")

        return 0

    except (IngestionError, ExecutionError) as e:
        log.error("Pipeline failed: %s", e)
        return 1
    except Exception as e:
        log.exception("Unexpected pipeline error: %s", e)
        return 1


def main() -> int:
    """Entry point for the pipeline."""
    config = load_config()
    setup_logging(config)

    dry_run = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")
    if dry_run:
        run_dry(config)
        return 0

    return run(config)


if __name__ == "__main__":
    sys.exit(main())
