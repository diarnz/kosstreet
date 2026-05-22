from __future__ import annotations

import httpx


class OpenRouterClient:
    """
    Thin HTTP wrapper around the OpenRouter chat completions endpoint.
    Owns no prompt logic — only knows how to send messages and return
    the raw model response string.
    """

    _HEADERS = {
        "Content-Type": "application/json",
        "HTTP-Referer": "https://kostreet.prizren.io",
        "X-Title": "KoStreet",
    }

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(
        self,
        messages: list[dict],
        response_format: dict | None = None,
    ) -> str:
        """
        Send a list of chat messages to the model and return the raw content
        string from the first choice.

        Raises httpx.HTTPStatusError on non-2xx responses.
        Raises httpx.TimeoutException if the request exceeds 30 seconds.
        """
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "response_format": response_format or {"type": "json_object"},
        }

        headers = {**self._HEADERS, "Authorization": f"Bearer {self.api_key}"}

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
