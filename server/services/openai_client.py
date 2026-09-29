"""OpenAI calls using SDK retries and application-level errors."""

import math

from flask import current_app
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, OpenAIError

from .exceptions import (
    ProviderConfigurationError,
    ProviderError,
    ProviderRequestError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


def get_openai_client():
    config = current_app.config
    api_key = config.get("OPENAI_API_KEY")
    if not isinstance(api_key, str) or not api_key.strip():
        raise ProviderConfigurationError("OPENAI_API_KEY is required for AI services.")

    timeout = config["OPENAI_TIMEOUT_SECONDS"]
    retries = config["OPENAI_MAX_RETRIES"]
    if timeout <= 0 or not math.isfinite(timeout):
        raise ProviderConfigurationError("OPENAI_TIMEOUT_SECONDS must be finite and positive.")
    if retries < 0:
        raise ProviderConfigurationError("OPENAI_MAX_RETRIES must be nonnegative.")

    return OpenAI(api_key=api_key.strip(), timeout=timeout, max_retries=retries)


"""
    Run a provider request in an app context and close the client afterward.
    The SDK handles retries; operation should contain only the provider request.
"""
def call_openai(operation):
    try:
        with get_openai_client() as client:
            return operation(client)
    except APITimeoutError as error:
        raise ProviderTimeoutError("AI provider request timed out.") from error
    except APIConnectionError as error:
        raise ProviderUnavailableError("AI provider is temporarily unavailable.") from error
    except APIStatusError as error:
        account_codes = (
            "insufficient_quota", "billing_hard_limit_reached", "billing_not_active",
            "account_deactivated", "invalid_api_key", "model_not_found",
        )
        if (
            error.status_code in (401, 403, 404)
            or error.code in account_codes
            or error.type in account_codes
        ):
            raise ProviderConfigurationError(
                "AI provider configuration or account requires attention."
            ) from error
        if error.status_code == 408:
            raise ProviderTimeoutError("AI provider request timed out.") from error
        if error.status_code == 429 or error.status_code >= 500:
            raise ProviderUnavailableError("AI provider is temporarily unavailable.") from error
        raise ProviderRequestError("AI provider rejected the request.") from error
    except OpenAIError as error:
        raise ProviderError("AI provider request failed.") from error
