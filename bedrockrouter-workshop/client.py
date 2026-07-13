"""
client.py — The ONLY place this project talks to BedrockRouter.

Read this file top to bottom once. Then notice during the workshop:
no matter which model you pick in the UI, NOTHING in this file changes.
The model ID is just one string inside the JSON payload.

BedrockRouter exposes an OpenAI-compatible endpoint:

    POST {BASE_URL}/v1/chat/completions
    Authorization: Bearer sk_m11_...

so the same code also works with the OpenAI SDK, the official
`bedrockrouter` SDK, LangChain, Vercel AI SDK, etc. We use raw
`requests` here so students can see the actual HTTP mechanics.
"""

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()  # reads .env in the project root

# Remove API_KEY from environment - will be provided by user via UI
BASE_URL = os.getenv("BEDROCKROUTER_BASE_URL", "").rstrip("/")
CHAT_PATH = "/v1/chat/completions"   # OpenAI-compatible route


class BedrockRouterError(Exception):
    """Raised with a human-readable message when a call fails."""


def build_payload(model_id: str, prompt: str,
                  temperature: float = 0.7, max_tokens: int = 1024) -> dict:
    """The exact JSON body sent to the API. Note what varies."""
    return {
        "model": model_id,   # <-- THE ONLY FIELD THAT EVER CHANGES
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def call_model(model_id: str, prompt: str,
               temperature: float = 0.7, max_tokens: int = 1024,
               api_key: str = "") -> dict:
    """
    Call any Bedrock model through BedrockRouter.

    Same endpoint. Same code. Different `model_id` -> different foundation model answers.
    API key MUST be provided by user through the frontend - no fallback to .env
    """
    if not api_key or not api_key.strip():
        raise BedrockRouterError(
            "❌ No API key provided. Please enter your BedrockRouter API key in the sidebar. "
            "Get your API key from: https://bedrockrouter.com/keys"
        )
    
    if not api_key.startswith("sk_m11_"):
        raise BedrockRouterError(
            "❌ Invalid API key format. BedrockRouter API keys should start with 'sk_m11_'"
        )
    
    if not BASE_URL:
        raise BedrockRouterError(
            "No base URL found. Copy .env.example to .env — the endpoint "
            "is pre-filled there."
        )

    payload = build_payload(model_id, prompt, temperature, max_tokens)
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }

    start = time.perf_counter()
    try:
        resp = requests.post(BASE_URL + CHAT_PATH, json=payload,
                             headers=headers, timeout=120)
    except requests.RequestException as exc:
        raise BedrockRouterError(f"Could not reach BedrockRouter: {exc}") from exc
    latency_s = round(time.perf_counter() - start, 2)

    if resp.status_code == 401:
        raise BedrockRouterError(
            f"❌ Invalid API key. Please check your BedrockRouter API key and try again."
        )
    elif resp.status_code == 403:
        raise BedrockRouterError(
            f"❌ Access forbidden. Your API key may not have permission to use model '{model_id}'."
        )
    elif resp.status_code != 200:
        raise BedrockRouterError(
            f"{model_id} -> HTTP {resp.status_code}: {resp.text[:400]}"
        )

    data = resp.json()
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise BedrockRouterError(f"Unexpected response shape: {data}") from exc

    usage = data.get("usage") or {}
    return {
        "text": text,
        "latency_s": latency_s,
        "input_tokens": usage.get("prompt_tokens", usage.get("input_tokens")),
        "output_tokens": usage.get("completion_tokens", usage.get("output_tokens")),
        "payload": payload,   # kept so the UI can prove what was sent
        "raw": data,
    }


if __name__ == "__main__":
    # Quick smoke test without the UI - requires API key as argument:  python client.py sk_m11_your_key_here
    import sys
    if len(sys.argv) < 2:
        print("Usage: python client.py <api_key>")
        print("Example: python client.py sk_m11_your_api_key_here")
        sys.exit(1)
    
    test_api_key = sys.argv[1]
    try:
        out = call_model("claude-haiku-4-5", "Say hello in five words.", api_key=test_api_key)
        print(f"✅ Success! [{out['latency_s']}s] {out['text']}")
    except BedrockRouterError as e:
        print(f"❌ Error: {e}")
