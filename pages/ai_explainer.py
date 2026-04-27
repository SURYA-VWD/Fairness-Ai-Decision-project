"""pages/ai_explainer.py"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.ui import nav_bar, page_header, require_analysis, go, PRIMARY, CARD, BORDER, MUTED, TEXT
from utils.ai_explainer import stream_explain, PRESET_QUESTIONS


def render():
    nav_bar("ai_explainer")
    if not require_analysis(): return
    page_header("AI Explainer", "Ask Gemini AI anything about your fairness analysis.")

    report = st.session_state.report

    # ── API key ────────────────────────────────────────────────────────────────
    if "api_key" not in st.session_state:
        st.session_state.api_key = "AIzaSyBvTixeuc2LoCrQAuxpwpy43RAubrutFPM"

    with st.expander("🔑 Google Gemini API Key", expanded=False):
        key_in = st.text_input("API key", type="password",
                               value=st.session_state.api_key,
                               placeholder="AIza…", label_visibility="collapsed")
        if key_in and key_in != st.session_state.api_key:
            st.session_state.api_key = key_in
            st.success("Key saved for this session.")

    api_key = st.session_state.api_key
    if not api_key:
        st.info("Enter your Google Gemini API key above to enable AI explanations.")
        return

    # ── Quick questions ────────────────────────────────────────────────────────
    st.markdown(f'<div class="fl-section">Quick questions</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    question_to_ask = None
    for i, q in enumerate(PRESET_QUESTIONS):
        with cols[i % 3]:
            if st.button(q[:52]+"…" if len(q)>52 else q, key=f"pq_{i}"):
                question_to_ask = q

    # ── Chat ───────────────────────────────────────────────────────────────────
    st.markdown(f'<div class="fl-section">Conversation</div>', unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chat_history and not question_to_ask:
        st.markdown(f"""
        <div style="background:{CARD};border:1px solid {PRIMARY}44;border-radius:14px;
             padding:1.1rem 1.3rem;font-size:.9rem;color:{MUTED};line-height:1.7">
            👋 Hi! I'm FairLens AI — powered by Gemini. I have full context of your bias report.
            Ask me to explain any metric, flag, or recommendation, or use the quick questions above.
        </div>""", unsafe_allow_html=True)

    for turn in st.session_state.chat_history:
        with st.chat_message(turn["role"]):
            st.write(turn["content"])

    user_input = st.chat_input("Ask about your bias report…")
    if user_input:
        question_to_ask = user_input

    if question_to_ask:
        _ask(question_to_ask, report, api_key)

    if st.session_state.chat_history:
        if st.button("🗑️ Clear chat"):
            st.session_state.chat_history = []
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Recommendations"):
        go("recommendations")


def _ask(question, report, api_key):
    st.session_state.chat_history.append({"role":"user","content":question})
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        history = [{"role":t["role"],"content":t["content"]}
                   for t in st.session_state.chat_history[:-1]]
        try:
            response = st.write_stream(stream_explain(question, report, api_key, history))
        except Exception as e:
            response = f"⚠️ Error: {e}"
            st.error(response)
    st.session_state.chat_history.append({"role":"assistant","content":response})
