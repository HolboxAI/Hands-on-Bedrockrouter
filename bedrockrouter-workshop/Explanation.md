# 📋 BedrockRouter Workshop - Complete Project Explanation

## 🎯 Project Overview

This project demonstrates **BedrockRouter**, a unified API gateway that allows you to access multiple AI models (Claude, GPT, Llama, etc.) through a single endpoint. The key insight is:

> **Change ONE string (model ID) → Access ANY AI model**  
> Same code, same endpoint, same API key, different model responses!

## 🏗️ Architecture & Design Philosophy

### Core Principle: **Separation of Concerns**
The project is intentionally split into exactly **3 files** to demonstrate clean architecture:

```
📁 bedrockrouter-workshop/
├── models.py      # 🎯 Model catalog (just strings!)
├── client.py      # 🔌 API communication (one function)
├── app.py         # 🖥️  User interface (Streamlit UI)
└── .env          # ⚙️  Configuration (base URL only)
```

### Why This Matters
In typical AI integration projects, model-specific code spreads everywhere:
- Different SDKs for different providers
- Different authentication methods
- Different request/response formats
- Different error handling

**BedrockRouter eliminates all of this complexity.**

## 📁 File-by-File Breakdown

### 1. `models.py` - The Model Catalog
```python
MODELS = {
    "Claude Sonnet 4.6":        "claude-sonnet-4-6",
    "Amazon Nova Pro":          "amazon.nova-pro-v1:0",
    "Llama 4 Maverick 17B":     "meta.llama4-maverick-17b-instruct-v1:0",
    # ... more models
}
```

**Purpose:** Maps friendly display names to official model IDs
- **Input:** Human-readable names for the UI dropdown
- **Output:** Official model identifiers for the API
- **Key Insight:** Adding a new AI model = adding ONE line here

### 2. `client.py` - The API Client
```python
def call_model(model_id: str, prompt: str, api_key: str, 
               temperature: float = 0.7, max_tokens: int = 1024) -> dict:
    # Builds OpenAI-compatible request
    # Sends to BedrockRouter endpoint
    # Returns standardized response
```

**Purpose:** Single function that talks to BedrockRouter
- **Input:** Model ID, prompt, parameters, user's API key
- **Process:** Creates OpenAI-compatible HTTP request
- **Output:** Standardized response with text, tokens, latency
- **Key Insight:** This function NEVER changes when you switch models

### 3. `app.py` - The User Interface
**Purpose:** Streamlit web app for testing and demonstration
- **API Key Management:** Users enter keys through UI (no file editing)
- **Single Model Mode:** Test one model at a time
- **Compare Mode:** Run two models in parallel with same prompt
- **Request Inspection:** Shows exact JSON payloads sent to API
- **Key Insight:** UI logic is completely independent of model choice

### 4. `.env` - Configuration
```bash
# No API key stored - users provide via UI
BEDROCKROUTER_BASE_URL=https://...amazonaws.com
```
**Purpose:** Only stores the BedrockRouter endpoint URL

## 🔄 How It All Works Together

### User Journey Flow:
1. **Start App:** `streamlit run app.py`
2. **Enter API Key:** User pastes key in sidebar
3. **Choose Model:** Select from dropdown (populated from `models.py`)
4. **Write Prompt:** Enter question/request
5. **Generate:** App calls `client.call_model()` with selected model ID
6. **View Results:** Response, metrics, and request payload

### Technical Flow:
```
User Input → app.py → models.py (lookup) → client.py → BedrockRouter API
    ↓
Response ← app.py ← client.py ← BedrockRouter API
```

### The Magic Moment:
When you switch from "Claude Sonnet" to "Amazon Nova":
- **models.py:** Different string returned (`"claude-sonnet-4-6"` → `"amazon.nova-pro-v1:0"`)
- **client.py:** Same function, same logic, different `model` field in JSON
- **app.py:** Same UI, same workflow, same display logic
- **Result:** Completely different AI model responding!

## 🔑 API Key Security Implementation

### Design Decision: Frontend API Key Entry
Instead of storing API keys in files, users enter them through the UI:

**Benefits:**
- ✅ No sensitive data in version control
- ✅ Easy to switch between different keys
- ✅ No file editing required
- ✅ Works in deployed environments

**Implementation:**
```python
# client.py - Validates and uses user-provided key
def call_model(..., api_key: str, ...):
    if not api_key or not api_key.startswith("sk_m11_"):
        raise BedrockRouterError("Please provide API key")
    
    headers = {"Authorization": f"Bearer {api_key}"}
```

**UI Flow:**
- Empty key → Friendly "Enter your bedrock-router API key here"
- Invalid format → Warning with format guidance  
- Valid key → Success indicator with masked key
- No key + button click → "Please provide API key"

## 🎮 Interactive Features

### 1. Single Model Mode
**Purpose:** Test individual models
- Select model from dropdown
- Enter prompt
- Click "✨ Generate"
- View response + metrics
- **Inspect payload** to see exact API request

### 2. Compare Mode  
**Purpose:** Direct model comparison
- Select two different models
- Same prompt sent to both **in parallel**
- Side-by-side results
- **Payload diff** proves only `model` field changed
- Performance comparison (latency, token usage)

### 3. Request Inspection
**Educational Feature:** Shows the actual HTTP request
```json
{
  "model": "claude-sonnet-4-6",    // ← THE ONLY THING THAT CHANGES
  "messages": [{"role": "user", "content": "..."}],
  "temperature": 0.7,
  "max_tokens": 1024
}
```

## 🧪 Technical Deep Dive

### OpenAI-Compatible API
BedrockRouter exposes an OpenAI-compatible endpoint:
```
POST https://...amazonaws.com/v1/chat/completions
Authorization: Bearer sk_m11_...
Content-Type: application/json
```

This means the same code works with:
- Official BedrockRouter SDK
- OpenAI Python SDK (different base_url)
- Any OpenAI-compatible library
- Raw HTTP requests (cURL, requests, fetch)

### Error Handling Strategy
```python
# Graceful error handling with user-friendly messages
try:
    response = call_model(...)
except BedrockRouterError as e:
    st.error(str(e))  # Shows in UI, doesn't crash
```

### Parallel Execution
Compare mode uses Python's ThreadPoolExecutor:
```python
with ThreadPoolExecutor(max_workers=2) as pool:
    future_a = pool.submit(call_model, model_a, prompt)
    future_b = pool.submit(call_model, model_b, prompt)
    # Both requests fly simultaneously
```

## 🎯 Educational Value

### Key Lessons Demonstrated:

1. **API Gateway Benefits**
   - One endpoint for many services
   - Consistent interface despite different backends
   - Simplified integration complexity

2. **Clean Architecture**  
   - Separation of concerns (UI/Logic/Data)
   - Single responsibility principle
   - Easy to extend and maintain

3. **Model Agnosticism**
   - Same code works with any model
   - Easy A/B testing between models
   - Reduces vendor lock-in

4. **Production Patterns**
   - Proper error handling
   - Security (API key validation)
   - Performance measurement
   - Request/response inspection

## 🚀 Extension Ideas

### Easy Extensions:
1. **Add Model:** One line in `models.py`
2. **System Prompts:** Modify `client.build_payload()`
3. **Streaming:** Add `"stream": true` to payload
4. **Custom Parameters:** Add sliders to UI

### Advanced Extensions:
1. **Model Routing:** Route requests based on prompt type
2. **Cost Tracking:** Track tokens and estimated costs
3. **Response Caching:** Cache responses for repeated queries
4. **Batch Processing:** Process multiple prompts at once

## 📊 Workshop Learning Outcomes

After completing this workshop, participants understand:

1. **How AI API gateways work** - Unified access to multiple models
2. **Clean architecture patterns** - Separation of concerns in practice  
3. **OpenAI-compatible APIs** - Industry standard interface
4. **Model comparison techniques** - A/B testing different AI models
5. **Production deployment patterns** - Security, error handling, UI/UX

## 🎓 Real-World Applications

This pattern is used in production for:
- **Multi-model chatbots** - Route to best model for each query
- **AI model evaluation** - Compare performance across providers
- **Fallback systems** - Switch models if one fails
- **Cost optimization** - Use cheaper models when appropriate
- **Compliance** - Route sensitive data to specific providers

---

## 🏁 Conclusion

This BedrockRouter workshop demonstrates that **AI model integration doesn't have to be complex**. With the right architecture:

- **One API key** accesses dozens of models
- **One function** handles all model communication  
- **One interface** works with any AI provider
- **One line change** switches between completely different AI systems

The future of AI development is **model-agnostic architectures** that let you choose the best tool for each task without vendor lock-in or integration complexity.

**BedrockRouter makes this future available today.** 🚀