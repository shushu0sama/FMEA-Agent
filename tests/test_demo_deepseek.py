"""D4 provider contract: bounded requests and safe failures, no real network."""

import json

import httpx
import pytest


def envelope(content='{"rows": []}', **extra):
    return {
        "choices": [{"finish_reason": "stop", "message": {"content": content}}],
        **extra,
    }


def client_for(handler):
    from fmea_agent.adapters.llm.deepseek import DeepSeekLLMClient

    return DeepSeekLLMClient("test-token", httpx.Client(transport=httpx.MockTransport(handler)))


def test_provider_request_and_usage():
    from fmea_agent.application.demo_ports import DemoLLMClient

    def reply(request):
        body = json.loads(request.content)
        assert str(request.url) == "https://api.deepseek.com/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-token"
        assert body["model"] == "deepseek-v4-pro"
        assert body["response_format"] == {"type": "json_object"}
        assert body["thinking"] == {"type": "disabled"}
        assert body["stream"] is False and body["max_tokens"] == 4096
        assert "tools" not in body
        assert request.extensions["timeout"] == {
            "connect": 10.0,
            "read": 60.0,
            "write": 60.0,
            "pool": 60.0,
        }
        return httpx.Response(
            200,
            json=envelope(
                model="deepseek-v4-pro",
                usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            ),
        )

    client = client_for(reply)
    assert isinstance(client, DemoLLMClient)
    assert client.generate("Return json") == '{"rows": []}'
    client.generate("Return json")
    assert client.usage()["request_count"] == 2
    assert client.usage()["total_tokens"] == 30
    assert client.usage()["response_model"] == "deepseek-v4-pro"
    assert client.usage()["called_at"]
    assert "test-token" not in repr(client)


@pytest.mark.parametrize(
    "status,code",
    [
        (401, "AUTH_FAILED"),
        (403, "AUTH_FAILED"),
        (400, "REQUEST_FAILED"),
        (500, "REQUEST_FAILED"),
        (302, "REQUEST_FAILED"),
    ],
)
def test_no_retry_or_error_body_leak(status, code):
    from fmea_agent.application.demo_ports import DemoModelError

    client = client_for(lambda request: httpx.Response(status, text="private test-token"))
    with pytest.raises(DemoModelError) as error:
        client.generate("private input")
    assert error.value.code == code
    assert str(error.value) == code and error.value.__suppress_context__
    assert client.usage()["request_count"] == 1


@pytest.mark.parametrize("status", [429, 502, 503, 504])
def test_one_retry_and_global_budget(monkeypatch, status):
    from fmea_agent.adapters.llm import deepseek
    from fmea_agent.application.demo_ports import DemoModelError

    delays = []
    monkeypatch.setattr(deepseek.time, "sleep", delays.append)
    count = 0

    def reply(request):
        nonlocal count
        count += 1
        return (
            httpx.Response(status, headers={"Retry-After": "9999"})
            if count % 2
            else (httpx.Response(200, json=envelope()))
        )

    client = client_for(reply)
    for _ in range(3):
        client.generate("json")
    with pytest.raises(DemoModelError, match="CALL_BUDGET_EXCEEDED"):
        client.generate("json")
    assert count == 6 and len(delays) == 3 and all(0 <= delay <= 2 for delay in delays)


def test_persistent_retryable_failure_stops_at_two(monkeypatch):
    from fmea_agent.adapters.llm import deepseek
    from fmea_agent.application.demo_ports import DemoModelError

    monkeypatch.setattr(deepseek.time, "sleep", lambda _: None)
    client = client_for(lambda _: httpx.Response(429))
    with pytest.raises(DemoModelError, match="RATE_LIMITED"):
        client.generate("json")
    assert client.usage()["request_count"] == 2


@pytest.mark.parametrize(
    "exception,code",
    [
        (httpx.ReadTimeout, "TIMEOUT"),
        (httpx.ConnectTimeout, "TIMEOUT"),
        (httpx.ConnectError, "CONNECTION_FAILED"),
    ],
)
def test_transport_failures_are_safe(exception, code):
    from fmea_agent.application.demo_ports import DemoModelError

    def fail(request):
        raise exception("private test-token")

    client = client_for(fail)
    with pytest.raises(DemoModelError, match=code) as error:
        client.generate("json")
    assert str(error.value) == code and client.usage()["request_count"] == 1


@pytest.mark.parametrize(
    "payload",
    [
        envelope(""),
        envelope("  "),
        envelope(None),
        envelope("not json"),
        envelope("[]"),
        envelope('{"x": NaN}'),
        envelope('{"x": 1, "x": 2}'),
        {"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]},
        {"choices": []},
        {"choices": [1]},
        envelope("{}", usage={"total_tokens": True}),
        {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": "{}", "tool_calls": [{"function": "write"}]},
                }
            ]
        },
    ],
)
def test_invalid_response_never_retried(payload):
    from fmea_agent.application.demo_ports import DemoModelError

    client = client_for(lambda _: httpx.Response(200, json=payload))
    with pytest.raises(DemoModelError, match="INVALID_RESPONSE"):
        client.generate("json")
    assert client.usage()["request_count"] == 1


def test_response_size_is_bounded_and_stream_closed():
    from fmea_agent.application.demo_ports import DemoModelError

    class Stream(httpx.SyncByteStream):
        reads = 0
        closed = False

        def __iter__(self):
            for _ in range(100):
                self.reads += 1
                yield b" " * 65536

        def close(self):
            self.closed = True

    stream = Stream()
    client = client_for(lambda _: httpx.Response(200, stream=stream))
    with pytest.raises(DemoModelError, match="INVALID_RESPONSE"):
        client.generate("json")
    assert stream.reads <= 17 and stream.closed


def test_missing_config_and_injected_client_lifecycle(monkeypatch):
    from fmea_agent.adapters.llm.deepseek import DeepSeekLLMClient
    from fmea_agent.application.demo_ports import DemoModelError

    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(DemoModelError, match="CONFIG_MISSING"):
        DeepSeekLLMClient.from_env()
    http = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200)))
    with DeepSeekLLMClient("test-token", http):
        pass
    assert not http.is_closed
    http.close()


def test_retry_cannot_exceed_sixth_request(monkeypatch):
    from fmea_agent.adapters.llm import deepseek
    from fmea_agent.application.demo_ports import DemoModelError

    delays = []
    monkeypatch.setattr(deepseek.time, "sleep", delays.append)
    calls = []

    def reply(request):
        calls.append(request)
        return httpx.Response(429) if len(calls) == 6 else httpx.Response(200, json=envelope())

    client = client_for(reply)
    for _ in range(5):
        client.generate("json")
    with pytest.raises(DemoModelError, match="CALL_BUDGET_EXCEEDED"):
        client.generate("json")
    assert len(calls) == 6 and not delays


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(200, content=b"\xff"),
        httpx.Response(200, content=b"not json"),
        httpx.Response(200, content=b"{}", headers={"content-length": "1048577"}),
        httpx.Response(200, content=b"{}", headers={"content-length": "bad"}),
        httpx.Response(200, content=b"{}", headers={"content-encoding": "identity,identity"}),
        httpx.Response(200, json=envelope("{}", model="untrusted secret value")),
    ],
)
def test_invalid_wire_envelope(response):
    from fmea_agent.application.demo_ports import DemoModelError

    with pytest.raises(DemoModelError, match="INVALID_RESPONSE"):
        client_for(lambda _: response).generate("json")


def test_owned_client_close_and_absent_usage():
    from fmea_agent.adapters.llm.deepseek import DeepSeekLLMClient
    from fmea_agent.application.demo_ports import DemoModelError

    client = client_for(lambda _: httpx.Response(200, json=envelope()))
    client.generate("json")
    assert client.usage()["total_tokens"] is None
    snapshot = client.usage()
    snapshot["request_count"] = 100
    assert client.usage()["request_count"] == 1
    with DeepSeekLLMClient("test-token") as owned:
        pass
    assert owned._http.is_closed
    with pytest.raises(DemoModelError, match="CLOSED"):
        owned.generate("json")


@pytest.mark.parametrize("key", [" ", "bad\nkey", "中文", "\x00"])
def test_invalid_key_is_safe(key):
    from fmea_agent.adapters.llm.deepseek import DeepSeekLLMClient
    from fmea_agent.application.demo_ports import DemoModelError

    with pytest.raises(DemoModelError) as error:
        DeepSeekLLMClient(key)
    assert str(error.value) in {"CONFIG_MISSING", "CONFIG_INVALID"}
