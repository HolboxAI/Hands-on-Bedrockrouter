"""
app.py — Streamlit UI for the BedrockRouter workshop.

Run with:  streamlit run app.py

This file only does UI. All API logic lives in client.py (one function),
all models live in models.py (one dict). That separation IS the lesson.
"""

import inspect
import sys
from concurrent.futures import ThreadPoolExecutor

import streamlit as st

from client import (BASE_URL, CHAT_PATH, BedrockRouterError,
                    call_model)
from models import MODELS

# Guard: `python app.py` starts Streamlit in "bare mode" and floods the
# terminal with ScriptRunContext warnings. Catch it early instead.
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    if get_script_run_ctx(suppress_warning=True) is None:
        sys.exit("\nThis is a Streamlit app — start it with:\n\n"
                 "    streamlit run app.py\n")
except ImportError:
    pass  # internal API moved in some future version — never block the app

st.set_page_config(page_title="BedrockRouter Playground",
                   page_icon="🔀", layout="wide")

st.title("🔀 BedrockRouter Playground")
st.caption("One endpoint · One API key · Any Bedrock model — "
           "only the **model ID** changes.")

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("🔑 API Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Enter your bedrock-router API key here",
        type="password",
        placeholder="sk_m11_your_api_key_here",
        help="Get your API key from: https://bedrockrouter.com/keys"
    )
    
    # API Key validation and status
    if api_key:
        api_key = api_key.strip()
        if api_key.startswith("sk_m11_"):
            st.success(f"✅ API key connected (…{api_key[-4:]})")
        else:
            st.warning("⚠️ Invalid key format. Should start with 'sk_m11_'")
    else:
        st.info("👆 Enter your BedrockRouter API key above to get started")
    
    st.divider()
    
    st.header("Settings")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1,
                            help="Higher = more creative, lower = more focused")
    max_tokens = st.slider("Max tokens", 128, 4096, 1024, 128)

    st.divider()
    st.subheader("Connection")
    st.caption("Every model below is called through this single URL:")
    st.code(f"POST {BASE_URL or '<set BEDROCKROUTER_BASE_URL>'}{CHAT_PATH}",
            language=None, wrap_lines=True)
    st.caption("The key is sent in the `Authorization` header — "
               "it never appears in the request payload.")
    st.caption("Model catalog: [bedrockrouter.com/models]"
               "(https://bedrockrouter.com/models)")
    
    # Instructions
    st.divider()
    st.subheader("📋 How to get API Key:")
    st.markdown("""
    1. Visit [bedrockrouter.com](https://bedrockrouter.com)
    2. Sign up or Login to your account
    3. Navigate to **API Keys** section  
    4. Click **Create new API key**
    5. Copy the key and paste it above 🔑
    
    **Note:** Your API key is only used in your browser session and is never stored.
    """)


def render_result(result: dict) -> None:
    """Metrics + response text for one model call."""
    c1, c2, c3 = st.columns(3)
    c1.metric("Latency", f"{result['latency_s']} s")
    c2.metric("Input tokens", result["input_tokens"] or "—")
    c3.metric("Output tokens", result["output_tokens"] or "—")
    st.markdown(result["text"])


# ---------------------------------------------------------------- main UI
mode = st.radio("Mode", ["Single model", "Compare two models"],
                horizontal=True, label_visibility="collapsed")

prompt = st.text_area(
    "Prompt",
    value="Explain what an API gateway does to a first-year student, "
          "in three sentences.",
    height=110,
)

names = list(MODELS.keys())

# Remove the blocking - let users see the interface

# ================================================== MODE 1: single model
if mode == "Single model":
    model_name = st.selectbox("Model", names)
    st.caption(f"Model ID that will be sent: `{MODELS[model_name]}`")

    if st.button("✨ Generate", type="primary", use_container_width=True):
        # Check for API key before making the call
        if not api_key or not api_key.strip():
            st.error("Please provide API key")
        elif not api_key.startswith("sk_m11_"):
            st.error("Invalid API key format")
        else:
            with st.spinner(f"Calling {model_name}…"):
                try:
                    st.session_state["single"] = (
                        model_name,
                        call_model(MODELS[model_name], prompt,
                                   temperature, max_tokens,
                                   api_key=api_key),
                    )
                except BedrockRouterError as err:
                    st.session_state.pop("single", None)
                    st.error(str(err))

    if "single" in st.session_state:
        name, result = st.session_state["single"]
        st.subheader(name)
        render_result(result)

        with st.expander("🔍 Exact request that was sent"):
            st.caption("Change the model in the dropdown and run again — "
                       "then watch which line changes. (Spoiler: one.)")
            st.json(result["payload"])

# ============================================ MODE 2: compare two models
else:
    col_a, col_b = st.columns(2)
    pick_a = col_a.selectbox("Model A", names, index=0)
    pick_b = col_b.selectbox("Model B", names, index=1)

    if st.button("⚡ Run both with the SAME code", type="primary",
                 use_container_width=True):
        
        # Check for API key before making the calls
        if not api_key or not api_key.strip():
            st.error("Please provide API key")
        elif not api_key.startswith("sk_m11_"):
            st.error("Invalid API key format")
        else:
            def safe_call(model_id: str):
                """Run one call; return (result, error) so one failure
                doesn't hide the other model's answer."""
                try:
                    return call_model(model_id, prompt, temperature,
                                      max_tokens, api_key=api_key), None
                except BedrockRouterError as err:
                    return None, str(err)

            with st.spinner(f"Calling {pick_a} and {pick_b} in parallel…"):
                # Two threads = both requests fly at once. Same function,
                # same endpoint, same key — only the model_id argument differs.
                with ThreadPoolExecutor(max_workers=2) as pool:
                    fut_a = pool.submit(safe_call, MODELS[pick_a])
                    fut_b = pool.submit(safe_call, MODELS[pick_b])
                    st.session_state["compare"] = (
                        pick_a, pick_b, fut_a.result(), fut_b.result()
                    )

    if "compare" in st.session_state:
        name_a, name_b, (res_a, err_a), (res_b, err_b) = \
            st.session_state["compare"]

        col_a, col_b = st.columns(2, gap="large")
        for col, name, res, err in ((col_a, name_a, res_a, err_a),
                                    (col_b, name_b, res_b, err_b)):
            with col:
                st.subheader(name)
                st.caption(f"`{MODELS.get(name, '?')}`")
                if err:
                    st.error(err)
                else:
                    render_result(res)

        # ---------------- the proof: diff the two request payloads
        if res_a and res_b:
            pay_a, pay_b = res_a["payload"], res_b["payload"]
            diff = sorted(k for k in set(pay_a) | set(pay_b)
                          if pay_a.get(k) != pay_b.get(k))
            same = sorted(set(pay_a) - set(diff))
            st.success(
                f"**Proof:** the two requests were identical in "
                f"`{'`, `'.join(same)}` — the only field that differed "
                f"was **`{'`, `'.join(diff)}`**."
            )
            with st.expander("🔍 See both request payloads"):
                d1, d2 = st.columns(2)
                d1.json(pay_a)
                d2.json(pay_b)
            with st.expander("🧩 The one function that made both calls"):
                st.code(inspect.getsource(call_model), language="python")
