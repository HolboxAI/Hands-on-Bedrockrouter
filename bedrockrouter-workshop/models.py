"""
models.py — The model catalog.

THE ENTIRE LESSON LIVES IN THIS FILE:
Every entry below is just a string. Switching models means passing a
different string to the API. Nothing else in this project changes.

    "Friendly name shown in the UI"  ->  "model ID sent to BedrockRouter"

These IDs are the official aliases from the BedrockRouter SDK
(pip install bedrockrouter -> bedrockrouter.Models). Full catalog:
https://bedrockrouter.com/models

WORKSHOP CHALLENGE #1: add one more model to this dict, save, and
watch it appear in the dropdown. That is the whole integration.
"""

MODELS = {
    # ---- Anthropic ----
    "Claude Sonnet 4.6":        "claude-sonnet-4-6",
    "Claude Haiku 4.5":         "claude-haiku-4-5",

    # ---- Amazon ----
    "Amazon Nova Pro":          "amazon.nova-pro-v1:0",
    "Amazon Nova Micro":        "amazon.nova-micro-v1:0",

    # ---- Meta ----
    "Llama 4 Maverick 17B":     "meta.llama4-maverick-17b-instruct-v1:0",

    # ---- MiniMax ----
    "MiniMax M2.5":             "minimax-m2.5",

    # ---- Mistral ----
    "Mistral Large 3":          "mistral.mistral-large-3-v1:0",

    # ---- DeepSeek ----
    "DeepSeek V3.2":            "deepseek.v3.2",

    # Add your own below (Challenge #1). A few ideas:
    #   "Kimi K2.6":            "kimi-k2.6",
    #   "Qwen3 Next 80B":       "qwen.qwen3-next-80b-a3b",
    #   "Nova Lite":            "amazon.nova-lite-v1:0",
    #   "GLM 5":                "zai.glm-5",
}
