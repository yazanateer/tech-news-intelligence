from types import SimpleNamespace

import pytest
from openai import OpenAIError
from twilio.base.exceptions import TwilioRestException

from app.services.ai.openai_client import AIClientError, OpenAIClient
from app.services.delivery.whatsapp_sender import DeliveryError, WhatsAppSender


class FakeResponses:
    def __init__(self, output_text: str = "", error: Exception = None) -> None:
        self.output_text = output_text
        self.error = error
        self.kwargs = {}

    def create(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return SimpleNamespace(output_text=self.output_text)


def _openai_client(responses: FakeResponses) -> OpenAIClient:
    return OpenAIClient(client=SimpleNamespace(responses=responses), model="test-model")


def test_generate_json_parses_output_and_sends_schema() -> None:
    responses = FakeResponses(output_text='{"ok": true}')

    result = _openai_client(responses).generate_json("sys", "user", "schema", {"type": "object"})

    assert result == {"ok": True}
    assert responses.kwargs["text"]["format"]["type"] == "json_schema"
    assert responses.kwargs["text"]["format"]["strict"] is True


def test_generate_json_raises_on_invalid_json() -> None:
    client = _openai_client(FakeResponses(output_text="not json"))

    with pytest.raises(AIClientError):
        client.generate_json("sys", "user", "schema", {})


def test_generate_json_wraps_api_errors() -> None:
    client = _openai_client(FakeResponses(error=OpenAIError("boom")))

    with pytest.raises(AIClientError):
        client.generate_json("sys", "user", "schema", {})


class FakeMessages:
    def __init__(self, error: Exception = None) -> None:
        self.error = error
        self.sent = []

    def create(self, **kwargs):
        if self.error:
            raise self.error
        self.sent.append(kwargs)
        return SimpleNamespace(sid="SM123")


def test_send_message_returns_sid() -> None:
    messages = FakeMessages()
    sender = WhatsAppSender(client=SimpleNamespace(messages=messages))

    assert sender.send_message("hello") == "SM123"
    assert messages.sent[0]["body"] == "hello"


def test_send_message_wraps_twilio_errors() -> None:
    error = TwilioRestException(status=400, uri="/Messages", msg="bad number")
    sender = WhatsAppSender(client=SimpleNamespace(messages=FakeMessages(error=error)))

    with pytest.raises(DeliveryError):
        sender.send_message("hello")


def test_openai_client_uses_configured_timeout(monkeypatch) -> None:
    monkeypatch.setattr("app.core.config.settings.openai_timeout_seconds", 12.5)
    monkeypatch.setattr("app.core.config.settings.openai_api_key", "test-key")

    client = OpenAIClient()

    assert client.client.timeout == 12.5
