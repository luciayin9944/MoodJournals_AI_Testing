"""Shared OpenAI calls with explicit timeouts and bounded, selective retries."""

import math
import random
import time
from collections.abc import Callable, Mapping
from datetime import timezone
from email.utils import parsedate_to_datetime
from typing import TypeVar

from flask import current_app
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    OpenAIError,
)

from .exceptions import (
    ProviderConfigurationError,
    ProviderError,
    ProviderRequestError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


_Result = TypeVar("_Result")
_MAX_RETRY_DELAY_SECONDS = 30.0
_CONFIGURATION_ERROR_CODES = {
    "insufficient_quota",
    "billing_hard_limit_reached",
    "billing_not_active",
    "account_deactivated",
    "invalid_api_key",
    "model_not_found",
}


def _validate_provider_config(config: Mapping) -> None:
    api_key = config.get("OPENAI_API_KEY")
    if not isinstance(api_key, str) or not api_key.strip():
        raise ProviderConfigurationError("OPENAI_API_KEY is required for AI services.")

    timeout = config.get("OPENAI_TIMEOUT_SECONDS")
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise ProviderConfigurationError(
            "OPENAI_TIMEOUT_SECONDS must be a finite positive number."
        )

    retries = config.get("OPENAI_MAX_RETRIES")
    if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
        raise ProviderConfigurationError(
            "OPENAI_MAX_RETRIES must be a nonnegative integer."
        )


def get_openai_client() -> OpenAI:
    """Create a client on demand; its caller owns closing it.

    Use inside a Flask application context, including in CLI scripts. Timeouts
    apply to HTTP operations, not to the total duration of all retry attempts.
    """
    config = current_app.config
    _validate_provider_config(config)
    try:
        return OpenAI(
            api_key=config["OPENAI_API_KEY"].strip(),
            timeout=float(config["OPENAI_TIMEOUT_SECONDS"]),
            # call_openai owns retries, including quota/billing exclusions.
            max_retries=0,
        )
    except OpenAIError as error:
        raise _translate_provider_error(error) from error


def _is_configuration_error(error: OpenAIError) -> bool:
    if isinstance(error, APIStatusError) and error.status_code in (401, 403, 404):
        return True
    return any(
        isinstance(value, str) and value in _CONFIGURATION_ERROR_CODES
        for value in (getattr(error, "code", None), getattr(error, "type", None))
    )


def _is_retryable(error: OpenAIError) -> bool:
    if _is_configuration_error(error):
        return False
    if isinstance(error, APIConnectionError):
        # APITimeoutError is also an APIConnectionError.
        return True
    if isinstance(error, APIStatusError):
        if error.response.headers.get("x-should-retry", "").lower() == "false":
            return False
        return error.status_code in (408, 429) or 500 <= error.status_code < 600
    return False


def _get_retry_delay(error: OpenAIError, retry_number: int) -> float | None:
    """Return a delay, or None when the provider requests an excessive wait."""
    if isinstance(error, APIStatusError):
        headers = error.response.headers
        for name, scale in (("retry-after-ms", 0.001), ("retry-after", 1.0)):
            value = headers.get(name)
            if value is None:
                continue
            try:
                delay = float(value) * scale
            except ValueError:
                if name != "retry-after":
                    continue
                try:
                    retry_at = parsedate_to_datetime(value)
                    if retry_at.tzinfo is None:
                        retry_at = retry_at.replace(tzinfo=timezone.utc)
                    delay = max(0.0, retry_at.timestamp() - time.time())
                except (TypeError, ValueError, OverflowError):
                    continue
            if not math.isfinite(delay) or delay < 0:
                continue
            # Do not cap a server-specified wait and then retry too early.
            return delay if delay <= _MAX_RETRY_DELAY_SECONDS else None

    # Bound the exponent too, even if a very large retry count is configured.
    backoff = min(0.5 * 2 ** min(retry_number, 10), _MAX_RETRY_DELAY_SECONDS)
    return random.uniform(backoff * 0.75, backoff)


def _translate_provider_error(error: OpenAIError) -> ProviderError:
    if _is_configuration_error(error):
        return ProviderConfigurationError(
            "AI provider configuration or account requires attention."
        )
    if isinstance(error, APITimeoutError) or (
        isinstance(error, APIStatusError) and error.status_code == 408
    ):
        return ProviderTimeoutError("AI provider request timed out.")
    if isinstance(error, APIConnectionError) or (
        isinstance(error, APIStatusError)
        and (error.status_code == 429 or 500 <= error.status_code < 600)
    ):
        return ProviderUnavailableError("AI provider is temporarily unavailable.")
    if isinstance(error, APIStatusError) and 400 <= error.status_code < 500:
        return ProviderRequestError("AI provider rejected the request.")
    return ProviderError("AI provider request failed.")


def call_openai(operation: Callable[[OpenAI], _Result]) -> _Result:
    """Run one non-streaming provider operation with bounded retries.

    The callable receives the client and must contain only the provider request;
    database writes and other side effects must remain outside this retry loop.
    Raw SDK errors are retained as causes for debugging, not in public messages.
    """
    with get_openai_client() as client:
        max_retries = current_app.config["OPENAI_MAX_RETRIES"]
        for attempt in range(max_retries + 1):
            try:
                return operation(client)
            except OpenAIError as error:
                if attempt >= max_retries or not _is_retryable(error):
                    raise _translate_provider_error(error) from error
                delay = _get_retry_delay(error, attempt)
                if delay is None:
                    raise _translate_provider_error(error) from error
                time.sleep(delay)
