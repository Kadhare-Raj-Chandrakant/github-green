"""LeetCode GraphQL API ingestion — the primary problem source."""

from __future__ import annotations

import json
import logging
import random
import time
from typing import Any

import requests

from src.ingestion.base import ProblemFetcher, IngestionError
from src.models.problem import ProblemContext, Difficulty

log = logging.getLogger(__name__)

# GraphQL query to fetch today's challenge
DAILY_CHALLENGE_QUERY = """
query questionOfToday {
    activeDailyCodingChallengeQuestion {
        date
        link
        question {
            title
            titleSlug
            difficulty
            content
            exampleTestcases
            codeSnippets {
                lang
                langSlug
                code
            }
            topicTags {
                name
            }
        }
    }
}
"""

PROBLEM_QUERY = """
query questionData($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        title
        titleSlug
        difficulty
        content
        exampleTestcases
        codeSnippets {
            lang
            langSlug
            code
        }
        topicTags {
            name
        }
    }
}
"""


class LeetCodeFetcher(ProblemFetcher):
    """Fetches the LeetCode Problem of the Day via GraphQL."""

    def __init__(
        self,
        api_url: str = "https://leetcode.com/graphql",
        timeout: int = 30,
        language: str = "cpp",
    ):
        self.api_url = api_url
        self.timeout = timeout
        self.language = language
        self.session = requests.Session()
        # Standard browser headers to avoid blocking
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://leetcode.com/",
        })

    def fetch(self) -> ProblemContext:
        """Fetch the daily challenge from LeetCode."""
        log.info("Fetching LeetCode Problem of the Day...")
        try:
            payload = {"query": DAILY_CHALLENGE_QUERY}
            resp = self.session.post(
                self.api_url,
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()

            if "errors" in data:
                raise IngestionError(f"LeetCode API error: {data['errors']}")

            challenge = data.get("data", {}).get("activeDailyCodingChallengeQuestion")
            if not challenge:
                raise IngestionError("No daily challenge found in response")

            return self._parse_challenge(challenge)
        except requests.RequestException as e:
            raise IngestionError(f"Network error fetching LeetCode: {e}") from e

    def fetch_by_slug(self, title_slug: str) -> ProblemContext:
        """Fetch a specific problem by its slug (e.g., 'two-sum')."""
        log.info("Fetching problem by slug: %s", title_slug)
        try:
            payload = {
                "query": PROBLEM_QUERY,
                "variables": {"titleSlug": title_slug},
            }
            resp = self.session.post(
                self.api_url,
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()

            if "errors" in data:
                raise IngestionError(f"LeetCode API error: {data['errors']}")

            question = data.get("data", {}).get("question")
            if not question:
                raise IngestionError(f"Problem '{title_slug}' not found")

            return self._parse_question(question, title_slug)
        except requests.RequestException as e:
            raise IngestionError(f"Network error fetching {title_slug}: {e}") from e

    def _parse_challenge(self, challenge: dict) -> ProblemContext:
        """Parse the daily challenge response into ProblemContext."""
        question = challenge["question"]
        title_slug = question["titleSlug"]
        return self._parse_question(question, title_slug)

    def _parse_question(self, question: dict, title_slug: str) -> ProblemContext:
        """Parse a GraphQL question object into ProblemContext."""
        title = question["title"]
        difficulty = Difficulty(question["difficulty"])

        # Find matching code snippet for target language
        boilerplate = ""
        for snippet in question.get("codeSnippets", []):
            if snippet["langSlug"] == self.language:
                boilerplate = snippet["code"]
                break
            # Fallback: use first available snippet if language not found
            if not boilerplate:
                boilerplate = snippet["code"]

        # Parse example test cases
        raw_examples = question.get("exampleTestcases", "")
        examples = []
        if raw_examples:
            parts = raw_examples.strip().split("\n")
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    examples.append({
                        "input": parts[i],
                        "output": parts[i + 1],
                    })

        source_url = f"https://leetcode.com/problems/{title_slug}/"

        return ProblemContext(
            title=title,
            difficulty=difficulty,
            description=question.get("content", ""),
            constraints="",  # Extracted from description by LLM
            examples=examples,
            boilerplate=boilerplate,
            source_url=source_url,
            source="leetcode",
            language=self.language,
        )
