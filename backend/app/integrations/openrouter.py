import asyncio
from typing import Any

import httpx


class OpenRouterClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def chat_completion(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        timeout: int = 30,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": model, "messages": messages}

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await self._post_with_retry(client, headers=headers, payload=payload)

        data = response.json()
        return str(data["choices"][0]["message"]["content"])

    async def _post_with_retry(
        self,
        client: httpx.AsyncClient,
        *,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> httpx.Response:
        response = await client.post(self.base_url, headers=headers, json=payload)

        if response.status_code in {429, 503}:
            await asyncio.sleep(2)
            response = await client.post(self.base_url, headers=headers, json=payload)

        response.raise_for_status()
        return response
