"""Unit tests for SarvamLLM provider."""
from __future__ import annotations

import unittest.mock as mock
from app.providers import SarvamLLM


def test_sarvam_provider_headers_and_payload():
    provider = SarvamLLM(
        base_url="https://api.sarvam.ai",
        api_key="sk_test_key_123",
        model="sarvam-105b",
        max_output_tokens=512,
    )

    assert provider._session.headers.get("api-subscription-key") == "sk_test_key_123"

    mock_resp = mock.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Sarvam AI response text",
                }
            }
        ],
        "usage": {
            "prompt_tokens": 15,
            "completion_tokens": 25,
            "total_tokens": 40,
        },
    }

    with mock.patch.object(provider._session, "post", return_value=mock_resp) as mock_post:
        history = [{"role": "user", "content": "Previous question"}, {"role": "assistant", "content": "Previous answer"}]
        result = provider.generate("Be concise.", "Hello", history=history)

        assert result == "Sarvam AI response text"
        assert provider.get_last_usage()["total_tokens"] == 40

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.sarvam.ai/v1/chat/completions"
        json_body = kwargs["json"]
        assert json_body["model"] == "sarvam-105b"
        assert json_body["max_tokens"] == 512
        assert len(json_body["messages"]) == 4  # system + 2 history + user
        assert json_body["messages"][0]["role"] == "system"
        assert json_body["messages"][3]["content"] == "Hello"
