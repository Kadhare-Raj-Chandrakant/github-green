"""Git operations — staging, committing, and pushing changes."""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from src.models.problem import ProblemContext

log = logging.getLogger(__name__)


class GitManager:
    """Handles all git operations for the pipeline.

    Operates within the GitHub Actions runner context where:
    - GITHUB_TOKEN is available for authentication
    - git is pre-configured with the Actions bot identity
    """

    def __init__(
        self,
        repo_path: str | Path = ".",
        branch: str = "main",
        author_name: str = "GitHubGreenCard Bot",
        author_email: str = "bot@githubgreencard.dev",
    ):
        self.repo_path = Path(repo_path).resolve()
        self.branch = branch
        self.author_name = author_name
        self.author_email = author_email

    def commit_and_push(self, problem: ProblemContext) -> bool:
        """Stage, commit, and push the new solution directory.

        Args:
            problem: The problem context for the commit message.

        Returns:
            True if push succeeded, False if there was nothing to commit.
        """
        folder = problem.folder_name()
        output_path = self.repo_path / "LeetCode" / folder

        if not output_path.exists():
            log.warning("Output path does not exist: %s", output_path)
            return False

        # Stage the new directory
        self._run_git("add", str(output_path))
        log.debug("Staged: %s", output_path)

        # Check if there's anything to commit
        status = self._run_git("status", "--porcelain")
        if not status.strip():
            log.info("Nothing to commit — all files already tracked")
            return False

        # Commit
        commit_msg = problem.commit_message()
        self._run_git(
            "-c", f"user.name={self.author_name}",
            "-c", f"user.email={self.author_email}",
            "commit", "-m", commit_msg,
        )
        log.info("Committed: %s", commit_msg)

        # Push
        remote_url = self._get_authenticated_remote()
        if remote_url:
            self._run_git("push", remote_url, self.branch)
            log.info("Pushed to %s/%s", remote_url, self.branch)
        else:
            self._run_git("push", "origin", self.branch)
            log.info("Pushed to origin/%s", self.branch)

        return True

    def setup_git_config(self) -> None:
        """Ensure git user config is set (for environments without it)."""
        try:
            self._run_git("config", "user.name", self.author_name)
            self._run_git("config", "user.email", self.author_email)
            log.debug("Git user config set")
        except RuntimeError:
            log.warning("Could not set git user config")

    def _get_authenticated_remote(self) -> str | None:
        """Build an authenticated remote URL using GITHUB_TOKEN if available."""
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token:
            return None

        # Get the remote origin URL
        try:
            remote = self._run_git("remote", "get-url", "origin").strip()
            if remote.startswith("https://"):
                # Insert token into URL: https://x-access-token:TOKEN@github.com/...
                parts = remote.split("://", 1)
                if len(parts) == 2:
                    return f"{parts[0]}://x-access-token:{token}@{parts[1]}"
            return remote
        except RuntimeError:
            return None

    def _run_git(self, *args: str) -> str:
        """Run a git command and return stdout."""
        cmd = ["git"] + list(args)
        log.debug("Running: %s", " ".join(cmd))
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.repo_path),
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            log.error("Git command failed: %s\n%s", e.cmd, e.stderr)
            raise RuntimeError(f"Git error: {e.stderr}") from e
