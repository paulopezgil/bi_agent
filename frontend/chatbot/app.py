from __future__ import annotations

import os

import httpx
import streamlit as st

AGENT_BASE_URL = os.getenv("AGENT_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="AI Analyst Chatbot", page_icon="chart_with_upwards_trend", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.4rem; max-width: 1000px;}
    .title {font-size: 2rem; font-weight: 700; margin-bottom: .25rem;}
    .subtitle {color: #4b5563; margin-bottom: 1rem;}
    .chip {display:inline-block; padding:2px 10px; border-radius:999px; background:#e5f4ec; color:#14532d; font-size:.78rem; margin-right:8px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title">Autonomous BI Analyst</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask business questions in natural language and inspect SQL + retries.</div>', unsafe_allow_html=True)
st.markdown('<span class="chip">LangGraph Agent</span><span class="chip">MCP SQL Tools</span><span class="chip">PostgreSQL</span>', unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

with st.form("chat_form", clear_on_submit=True):
    user_message = st.text_input("Ask a question", placeholder="How many customers do we have?")
    submitted = st.form_submit_button("Send")

if submitted and user_message.strip():
    with st.spinner("Querying agent..."):
        try:
            response = httpx.post(
                f"{AGENT_BASE_URL}/chat",
                json={"message": user_message.strip()},
                timeout=30,
            )
            response.raise_for_status()
            payload: dict = response.json()
            st.session_state.history.append(
                {
                    "question": user_message.strip(),
                    "answer": payload.get("answer", ""),
                    "sql": payload.get("sql", ""),
                    "retries": payload.get("retries", 0),
                    "rows": payload.get("rows", []),
                    "error": payload.get("error", ""),
                }
            )
        except Exception as exc:  # pragma: no cover - UI fallback path
            st.session_state.history.append(
                {
                    "question": user_message.strip(),
                    "answer": "Agent request failed.",
                    "sql": "",
                    "retries": 0,
                    "rows": [],
                    "error": str(exc),
                }
            )

if not st.session_state.history:
    st.info("No messages yet. Ask your first BI question.")

for item in reversed(st.session_state.history):
    with st.container(border=True):
        st.markdown(f"**You:** {item['question']}")
        st.markdown(f"**Agent:** {item['answer']}")
        c1, c2 = st.columns([2, 1])
        c1.code(item["sql"] or "No SQL generated", language="sql")
        c2.metric("Retries", int(item["retries"]))
        if item["error"]:
            st.error(item["error"])
        elif item["rows"]:
            st.dataframe(item["rows"], use_container_width=True)
        else:
            st.caption("No rows returned.")
