"""Application-lifetime VectorAI connection management."""

from actian_vectorai import VectorAIClient

from constants import VECTORAI_HOST


class VectorAIConnection:
    """Own one VectorAI client for the lifetime of an API process."""

    def __init__(self) -> None:
        self._client: VectorAIClient | None = None

    def connect(self) -> VectorAIClient:
        """Open the client once and return the shared connected instance."""
        if self._client is None:
            client = VectorAIClient(VECTORAI_HOST)
            self._client = client.__enter__()
        return self._client

    def close(self) -> None:
        """Release client resources when the API process stops."""
        if self._client is not None:
            self._client.__exit__(None, None, None)
            self._client = None
