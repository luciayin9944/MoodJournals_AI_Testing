"""Provider failures that application services and API resources can handle."""


class ProviderError(Exception):
    """Base class for controlled AI provider failures."""


class ProviderConfigurationError(ProviderError):
    """Provider settings, credentials, model access, or account need attention."""


class ProviderTimeoutError(ProviderError):
    """The provider request ultimately timed out."""


class ProviderUnavailableError(ProviderError):
    """A temporary provider failure could not be recovered within retry limits."""


class ProviderRequestError(ProviderError):
    """The provider rejected the request as invalid."""
