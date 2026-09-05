"""Native HTTP logging must not disclose provider headers or private transport errors."""

import io
import logging
import threading

import httpcore
import httpx
import pytest

from fmea_agent.adapters.llm.deepseek import DeepSeekLLMClient
from fmea_agent.application.demo_ports import DemoModelError


@pytest.mark.parametrize("status", [200, 401])
def test_owned_native_http11_does_not_log_response_headers(status):
    output = io.StringIO()
    logger = logging.getLogger("httpcore.http11")
    handler = logging.StreamHandler(output)
    before = logger.level, logger.disabled, list(logger.filters), list(logger.handlers)
    logger.setLevel(logging.DEBUG)
    logger.disabled = False
    logger.addHandler(handler)
    body = b'{"choices":[{"finish_reason":"stop","message":{"content":"{}"}}]}'
    wire = (
        f"HTTP/1.1 {status} Result\r\nContent-Length: {len(body)}\r\n"
        "X-Error-Detail: SYNTHETIC_PRIVATE_ERROR\r\n\r\n"
    ).encode() + body
    try:
        with DeepSeekLLMClient("test-token") as client:
            client._http._transport._pool._network_backend = httpcore.MockBackend([wire])
            if status == 200:
                assert client.generate("json") == "{}"
            else:
                with pytest.raises(DemoModelError, match="AUTH_FAILED"):
                    client.generate("json")
        assert "SYNTHETIC_PRIVATE_ERROR" not in output.getvalue()
        assert logger.level == logging.DEBUG and not logger.disabled
        assert logger.filters == before[2]
        logger.debug("restored")
        assert "restored" in output.getvalue()
    finally:
        logger.removeHandler(handler)
        logger.setLevel(before[0])
        logger.disabled = before[1]


@pytest.mark.parametrize("exception", [httpx.ReadTimeout, RuntimeError, KeyboardInterrupt])
def test_filter_restores_after_exceptions_and_preserves_unrelated_logging(exception):
    output = io.StringIO()
    native = logging.getLogger("httpcore.connection")
    app = logging.getLogger("demo-test-unrelated")
    handler = logging.StreamHandler(output)
    before = [(logger.level, logger.disabled, list(logger.filters)) for logger in [native, app]]
    for logger in [native, app]:
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.disabled = False

    def reply(request):
        native.debug("SYNTHETIC_PRIVATE_ERROR")
        app.debug("unrelated-app-log")
        thread = threading.Thread(target=lambda: native.debug("unrelated-thread-log"))
        thread.start()
        thread.join()
        raise exception("SYNTHETIC_PRIVATE_ERROR")

    http = httpx.Client(transport=httpx.MockTransport(reply))
    try:
        with DeepSeekLLMClient("test-token", http) as client:
            with pytest.raises((DemoModelError, RuntimeError, KeyboardInterrupt)):
                client.generate("json")
        assert "SYNTHETIC_PRIVATE_ERROR" not in output.getvalue()
        assert "unrelated-app-log" in output.getvalue()
        assert "unrelated-thread-log" in output.getvalue()
        for logger, (_, _, filters) in zip([native, app], before, strict=True):
            assert logger.filters == filters
    finally:
        http.close()
        for logger, (level, disabled, _) in zip([native, app], before, strict=True):
            logger.removeHandler(handler)
            logger.setLevel(level)
            logger.disabled = disabled


def test_retry_filters_every_pinned_native_logger_and_restores_existing_filters(monkeypatch):
    from fmea_agent.adapters.llm import deepseek
    from fmea_agent.adapters.llm._logging import HTTP_LOGGER_NAMES

    output = io.StringIO()
    handler = logging.StreamHandler(output)
    loggers = [logging.getLogger(name) for name in HTTP_LOGGER_NAMES]
    before = [
        (logger.level, logger.disabled, list(logger.filters), list(logger.handlers))
        for logger in loggers
    ]
    old_threshold = logging.root.manager.disable
    calls = []
    delays = []
    monkeypatch.setattr(deepseek.time, "sleep", delays.append)
    for logger in loggers:
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.disabled = False

    def reply(request):
        calls.append(request)
        for logger in loggers:
            logger.debug("SYNTHETIC_PRIVATE_ERROR")
        return (
            httpx.Response(503)
            if len(calls) == 1
            else httpx.Response(
                200,
                json={
                    "choices": [{"finish_reason": "stop", "message": {"content": "{}"}}],
                },
            )
        )

    try:
        with httpx.Client(transport=httpx.MockTransport(reply)) as http:
            with DeepSeekLLMClient("test-token", http) as client:
                assert client.generate("json") == "{}"
        assert len(calls) == 2 and delays == [1.0]
        assert "SYNTHETIC_PRIVATE_ERROR" not in output.getvalue()
        assert logging.root.manager.disable == old_threshold
        for logger, (_, _, filters, handlers) in zip(loggers, before, strict=True):
            assert logger.filters == filters
            assert logger.handlers == [*handlers, handler]
    finally:
        for logger, (level, disabled, _, _) in zip(loggers, before, strict=True):
            logger.removeHandler(handler)
            logger.setLevel(level)
            logger.disabled = disabled
