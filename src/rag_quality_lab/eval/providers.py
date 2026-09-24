"""Run-scoped Ragas adapters and sanitized evaluator failures.

Call metrics through EvaluatorProviders.call so a fatal provider failure stops
later judging. The SDK alone retries transport failures; Ragas/Instructor repair
is disabled. Query providers and their authentication are deliberately separate.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from contextlib import AsyncExitStack, asynccontextmanager, contextmanager
from contextvars import ContextVar
from typing import Any

import httpx
from azure.core.exceptions import ClientAuthenticationError
from openai import APIStatusError, APITimeoutError, AsyncOpenAI
from pydantic import ValidationError

from rag_quality_lab.eval.config import EvalConfig, normalize_endpoint

_in_evaluator = ContextVar("in_evaluator", default=False)


@contextmanager
def _safe_provider_logs() -> Iterator[None]:
    # Instructor logs raw exceptions before our boundary can sanitize them.
    # The context flag leaves diagnostics from unrelated tasks/threads alone.
    def sanitize(record: logging.LogRecord) -> bool:
        if _in_evaluator.get():
            record.msg = "Evaluator provider diagnostic; see sanitized metric outcome"
            record.args = ()
            record.exc_info = record.exc_text = record.stack_info = None
        return True

    loggers = [
        logging.getLogger(name)
        for name in ("instructor.v2.retry", "openai._base_client")
    ]
    token = _in_evaluator.set(True)
    for logger in loggers:
        logger.addFilter(sanitize)
    try:
        yield
    finally:
        for logger in loggers:
            logger.removeFilter(sanitize)
        _in_evaluator.reset(token)


class EvalProviderError(Exception):
    """Only these fixed codes/messages may be serialized, never SDK exceptions."""

    def __init__(self, code: str, *, fatal: bool = False):
        self.code = code
        self.fatal = fatal
        super().__init__(f"Evaluator {code}")

    def as_dict(self) -> dict[str, str | bool]:
        return {"code": self.code, "message": str(self), "fatal": self.fatal}


def _provider_error(error: Exception) -> EvalProviderError:
    # Instructor wraps SDK/validation errors. Inspect types, never message text.
    pending = [error]
    seen = set()
    code = "provider_error"
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, EvalProviderError):
            return current
        if isinstance(current, ClientAuthenticationError):
            return EvalProviderError("authentication", fatal=True)
        if isinstance(current, APIStatusError):
            if current.status_code in (401, 403):
                return EvalProviderError("authentication", fatal=True)
            if current.status_code in (400, 404, 405, 422):
                return EvalProviderError("configuration", fatal=True)
        if isinstance(current, (APITimeoutError, TimeoutError)):
            code = "timeout"
        elif isinstance(current, (ValidationError, json.JSONDecodeError)):
            code = "invalid_output"
        pending.extend(
            cause
            for cause in (current.__cause__, current.__context__)
            if cause is not None
        )
        pending.extend(
            attempt.exception
            for attempt in getattr(current, "failed_attempts", None) or []
        )
    return EvalProviderError(code)


def _build_llm(config: EvalConfig, client: AsyncOpenAI) -> Any:
    try:
        from ragas.llms import llm_factory
    except ImportError:
        raise EvalProviderError(
            "missing eval extra: uv sync --locked --extra eval", fatal=True
        ) from None
    llm = llm_factory(
        config.model, client=client, max_retries=config.structured_output_retries
    )
    # Azure deployment names do not reveal model capabilities to Ragas.
    llm.model_args = {
        "max_completion_tokens": 4096,
        "max_retries": config.structured_output_retries,
    }
    return llm


class EvaluatorProviders:
    """Borrowed adapters plus a sequential, fail-closed metric-call boundary."""

    def __init__(self, config: EvalConfig, client: AsyncOpenAI):
        self.llm = _build_llm(config, client)
        self._lock = asyncio.Lock()
        self._stopped = False

    async def call[T](
        self, operation: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
    ) -> T:
        async with self._lock:
            if self._stopped:
                raise EvalProviderError("stopped", fatal=True)
            try:
                with _safe_provider_logs():
                    return await operation(*args, **kwargs)
            except Exception as exc:
                error = _provider_error(exc)
                self._stopped = error.fatal
                raise error from None


async def _close_owned(resource: Any) -> None:
    try:
        await resource.close()
    except Exception:
        raise EvalProviderError("cleanup", fatal=True) from None


@asynccontextmanager
async def evaluator_scope(
    config: EvalConfig, *, client: AsyncOpenAI | None = None, credential: Any = None
) -> AsyncIterator[EvaluatorProviders]:
    """Own created clients/credentials; injected resources remain caller-owned.

    An injected SDK client must already target the resolved endpoint and use the
    resolved timeout/retry policy. This avoids mutating a caller-owned client.
    """
    async with AsyncExitStack() as stack:
        try:
            if client is None:
                if config.api_key is not None:
                    api_key = config.api_key.get_secret_value()
                else:
                    from azure.identity.aio import (
                        DefaultAzureCredential,
                        get_bearer_token_provider,
                    )

                    if credential is None:
                        credential = DefaultAzureCredential()
                        stack.push_async_callback(_close_owned, credential)
                    api_key = get_bearer_token_provider(
                        credential, "https://cognitiveservices.azure.com/.default"
                    )
                client = AsyncOpenAI(
                    base_url=config.base_url,
                    api_key=api_key,
                    timeout=config.timeout_seconds,
                    max_retries=config.max_retries,
                )
                stack.push_async_callback(_close_owned, client)
            elif (
                normalize_endpoint(str(client.base_url)) != config.base_url
                or client.max_retries != config.max_retries
                or httpx.Timeout(client.timeout)
                != httpx.Timeout(config.timeout_seconds)
            ):
                raise EvalProviderError("configuration", fatal=True)
            evaluator = EvaluatorProviders(config, client)
        except Exception as exc:
            error = _provider_error(exc)
            if error.code == "provider_error":
                error = EvalProviderError("configuration", fatal=True)
            raise error from None
        yield evaluator
