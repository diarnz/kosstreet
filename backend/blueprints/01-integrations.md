# Phase 1 — Integrations

> **Files to create / modify:**
> - `app/integrations/openrouter.py` — new file
> - `app/integrations/street_imagery.py` — add GSV implementation to existing file
> - `app/integrations/__init__.py` — update exports

---

## What this phase does

Builds the two outbound HTTP clients the backend needs to talk to external services:

1. **OpenRouter** — sends images to the Gemma vision model and gets back civic issue analysis
2. **Google Street View** — fetches street-level JPEG frames given GPS coordinates and a camera angle

Both are thin, focused clients. They have no business logic — they just make HTTP calls and return data. The AI service (Phase 2) and Audit service (Phase 4) will use them.

---

## File 1: `app/integrations/openrouter.py`

### Purpose
Wraps the OpenRouter `/chat/completions` API. Accepts a model name and a list of message dicts, returns the raw text content from the first choice.

### Class: `OpenRouterClient`

```
OpenRouterClient(api_key: str)

async def chat_completion(
    model:    str,
    messages: list[dict],   ← standard OpenAI-format message list
    timeout:  int = 30,
) -> str                    ← raw content string from choices[0].message.content
```

### Behaviour
- Uses `httpx.AsyncClient` with `Authorization: Bearer {api_key}` header
- POST to `https://openrouter.ai/api/v1/chat/completions`
- Request body: `{"model": model, "messages": messages}`
- On HTTP 429 or 503: waits 2 seconds, retries once
- On any other non-2xx: raises `httpx.HTTPStatusError` (caller handles it)
- Timeout: configurable, default 30 seconds

### How a vision message looks (built by the AI service, not here)
```json
{
  "role": "user",
  "content": [
    {
      "type": "image_url",
      "image_url": { "url": "data:image/jpeg;base64,<b64_string>" }
    },
    {
      "type": "text",
      "text": "<the civic issue prompt>"
    }
  ]
}
```

---

## File 2: `app/integrations/street_imagery.py`

### Purpose
The Protocol `StreetImageryClient` and the `StreetImageryFrameRequest` / `StreetImageryFrame` dataclasses already exist in this file. This phase adds the concrete `GoogleStreetViewClient` implementation underneath them.

### Class: `GoogleStreetViewClient`

```
GoogleStreetViewClient(api_key: str, size: int = 640)

def fetch_frame(request: StreetImageryFrameRequest) -> StreetImageryFrame
```

### Behaviour
- Uses `httpx` **sync** client (the audit pipeline background task does not need async for this one call)
- GET `https://maps.googleapis.com/maps/api/streetview`
- Query params:
  - `size={size}x{size}` (default 640×640)
  - `location={latitude},{longitude}`
  - `heading={heading}`
  - `pitch={pitch}`
  - `key={api_key}`
- Returns `StreetImageryFrame(source="google_sv", content_type="image/jpeg", data=<bytes>)`
- If GSV returns a grey "no imagery" placeholder (HTTP 200 but content is the error image), the bytes are still returned — the AI service decides if the image contains anything useful
- On HTTP error: raises `httpx.HTTPStatusError`

---

## File 3: `app/integrations/__init__.py`

### Exports
```python
from app.integrations.openrouter import OpenRouterClient
from app.integrations.street_imagery import (
    GoogleStreetViewClient,
    StreetImageryClient,
    StreetImageryFrame,
    StreetImageryFrameRequest,
)
```

---

## What is NOT in this phase
- No business logic
- No database access
- No Pydantic models
- The prompt text lives in Phase 2 (AI service), not here
