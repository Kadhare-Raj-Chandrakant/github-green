"""Tests for the LLM client."""

from unittest.mock import Mock, patch

import pytest

from src.execution.llm_client import LLMClient
from src.execution.exceptions import ExecutionError


# Patch at the module where openai is imported
PATCH_PATH = "src.execution.llm_client.openai.OpenAI"


def _make_client(api_key="test-key", retry_count=2):
    """Helper to create an LLMClient inside a patched context."""
    return LLMClient(
        model="gpt-4o-mini",
        api_key=api_key,
        retry_count=retry_count,
        retry_delay=0,
    )


class TestLLMClient:
    def test_generate_success(self):
        """Successful LLM call should return the response content."""
        with patch(PATCH_PATH) as mock_openai_class:
            mock_instance = Mock()
            mock_openai_class.return_value = mock_instance

            mock_choice = Mock()
            mock_choice.message.content = "Hello world"
            mock_response = Mock()
            mock_response.choices = [mock_choice]
            mock_instance.chat.completions.create.return_value = mock_response

            client = _make_client()
            result = client.generate(
                system_prompt="You are helpful",
                user_prompt="Say hello",
            )
            assert result == "Hello world"

    def test_generate_retry_then_succeed(self):
        """Client should retry on API errors and succeed eventually."""
        with patch(PATCH_PATH) as mock_openai_class:
            mock_instance = Mock()
            mock_openai_class.return_value = mock_instance

            from openai import RateLimitError
            mock_instance.chat.completions.create = Mock(
                side_effect=[
                    RateLimitError("rate limited", response=Mock(status_code=429), body={}),
                    Mock(
                        choices=[
                            Mock(message=Mock(content="Success after retry"))
                        ]
                    ),
                ]
            )

            client = _make_client()
            result = client.generate(
                system_prompt="You are helpful",
                user_prompt="Say hello",
            )
            assert result == "Success after retry"
            assert mock_instance.chat.completions.create.call_count == 2

    def test_generate_all_retries_fail(self):
        """Client should raise ExecutionError after all retries exhausted."""
        with patch(PATCH_PATH) as mock_openai_class:
            mock_instance = Mock()
            mock_openai_class.return_value = mock_instance

            from openai import APIError
            mock_instance.chat.completions.create.side_effect = APIError(
                message="server error",
                request=Mock(),
                body={},
            )

            client = _make_client()
            with pytest.raises(ExecutionError, match="retries"):
                client.generate(
                    system_prompt="You are helpful",
                    user_prompt="Say hello",
                )
            assert mock_instance.chat.completions.create.call_count == 2
