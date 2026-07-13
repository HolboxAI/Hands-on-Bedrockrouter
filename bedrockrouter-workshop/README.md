# 🔀 BedrockRouter Workshop — One API, Every Model

A hands-on Streamlit app that proves one idea:

> **Same endpoint. Same API key. Same code. Change one string — the model ID —
> and you're talking to a completely different foundation model.**

## Project layout (3 Python files, on purpose)

| File | Role | Changes when you switch models? |
|---|---|---|
| `models.py` | Dict of friendly names → model IDs | ✅ Only here (and it's just strings) |
| `client.py` | ONE function that calls the API | ❌ Never |
| `app.py` | Streamlit UI | ❌ Never |

## Setup (≈5 minutes)

```bash
# 1. Create a virtual env (recommended)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
cp .env.example .env               # Windows: copy .env.example .env
#    → open .env and paste your key from https://bedrockrouter.com/keys

# 4. Run
streamlit run app.py
```

No key yet? Instructor will share one, or create your own at
**bedrockrouter.com → API Keys → Create key**.

## What to do in the app

1. **Single model** — type a prompt, pick a model, Generate.
   Open *"Exact request that was sent"*, switch model, run again,
   and spot the one line that changed.
2. **Compare two models** — same prompt goes to two models **in parallel**.
   The app diffs both request payloads live and shows the only
   differing field: `model`. Watch the latency/token metrics too —
   try *Nova Micro* vs *Claude Sonnet 4.6*.

## Suggested session flow (~50 min)

| Time | Activity |
|---|---|
| 5 min | Walk through the 3-file structure — where would model logic *usually* leak? |
| 10 min | Everyone: setup + `.env` + first Generate |
| 15 min | Free experimentation: same prompt across 4+ models; compare tone, speed, tokens |
| 10 min | Compare mode + payload diff — the "only `model` changed" proof |
| 10 min | Challenges below |

## Challenges (fast finishers)

1. **Add a model** — one line in `models.py` (ideas are commented in the file).
   Refresh the app: your model is in the dropdown. *That was the whole integration.*
2. **System prompt** — add a `st.text_input` in `app.py` and prepend
   `{"role": "system", "content": ...}` in `client.build_payload`.
   Works identically for every model.
3. **Streaming** — add `"stream": true` to the payload and iterate
   `resp.iter_lines()` over the SSE chunks (or see the SDK example below).
   Render with `st.write_stream`.

## The same call, three other ways

Because the endpoint is **OpenAI-compatible**, everything you built today
transfers directly:

**Official BedrockRouter SDK** (`pip install bedrockrouter`):
```python
from bedrockrouter import BedrockOpenAI, Models

client = BedrockOpenAI(api_key="sk_m11_...")
resp = client.chat.completions.create(
    model=Models.CLAUDE_SONNET_4_6,          # or any of 87 aliases
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=1024,
)
print(resp.choices[0].message.content)
```

**OpenAI SDK** — just point `base_url` at the proxy:
```python
from openai import OpenAI

client = OpenAI(api_key="sk_m11_...", base_url="<BASE_URL>/v1")
resp = client.chat.completions.create(model="amazon.nova-pro-v1:0",
                                      messages=[{"role": "user", "content": "Hi"}])
```

**cURL**:
```bash
curl -s $BEDROCKROUTER_BASE_URL/v1/chat/completions \
  -H "Authorization: Bearer $BEDROCKROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-haiku-4-5","messages":[{"role":"user","content":"Hi"}],"max_tokens":200}'
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| "No API key found" | `.env` missing or app started before you created it — restart Streamlit |
| HTTP 401 / 403 | Key typo, or key was revoked — check bedrockrouter.com/keys |
| HTTP 404 | `BEDROCKROUTER_BASE_URL` edited/truncated — re-copy from `.env.example` |
| Model error | ID typo in `models.py` — verify against bedrockrouter.com/models |
| Slow response | Big models take longer — that's part of the demo! Compare with Nova Micro |
