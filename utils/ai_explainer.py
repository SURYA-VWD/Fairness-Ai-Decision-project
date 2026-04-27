"""
utils/ai_explainer.py
Gemini-powered plain-language explanations of fairness results.
"""

import google.generativeai as genai
import streamlit as st
from typing import Optional


def _build_context(report) -> str:
    """Serialize the fairness report into a prompt-friendly context string."""
    lines = [
        "=== FAIRNESS ANALYSIS REPORT ===",
        f"Bias Score: {report.bias_score:.1f}/100 (higher = fairer)",
        f"Demographic Parity Ratio: {report.demographic_parity_ratio:.3f}",
        f"Disparate Impact Ratio:   {report.disparate_impact_ratio:.3f}",
        f"Equalized Odds Diff:      {report.equalized_odds_diff:.3f}",
        f"Equal Opportunity Diff:   {report.equal_opportunity_diff:.3f}",
        f"Overall Model Accuracy:   {report.overall_accuracy:.3f}",
        "",
        "=== GROUP STATISTICS ===",
    ]
    for g in report.group_stats:
        lines.append(
            f"  {g.name}: n={g.n}, positive_rate={g.positive_rate:.2f}, "
            f"TPR={g.tpr:.2f}, FPR={g.fpr:.2f}"
        )

    if report.proxy_features:
        lines.append("\n=== PROXY FEATURES DETECTED ===")
        for p in report.proxy_features:
            lines.append(f"  {p['feature']}: correlation={p['correlation']}, risk={p['risk']}")

    lines.append("\n=== FLAGGED ISSUES ===")
    for f in report.flags:
        lines.append(f"  [{f['severity']}] {f['title']}: {f['detail']}")

    return "\n".join(lines)


SYSTEM_PROMPT = """You are FairLens AI, an expert in machine learning fairness, 
algorithmic bias, and responsible AI. You help data scientists and non-technical 
stakeholders understand bias in ML models.

Your responses are:
- Clear and jargon-free for non-technical users
- Precise and actionable for data scientists
- Grounded in the fairness metrics provided
- Structured with bullet points when listing recommendations
- Concise (3-5 short paragraphs max unless asked for more)

When asked about technical metrics, briefly define them before explaining the result.
Always end with 1-2 concrete next steps tailored to the specific analysis."""


def _build_gemini_history(conversation_history: list) -> list:
    """Convert flat chat history to Gemini's contents format."""
    gemini_history = []
    for turn in conversation_history:
        role = "user" if turn["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [turn["content"]]})
    return gemini_history


def explain(
    question: str,
    report,
    api_key: str,
    conversation_history: Optional[list] = None,
) -> str:
    """
    Send a question + report context to Gemini and return the answer.
    Supports multi-turn conversation via conversation_history.
    """
    context = _build_context(report)
    system_with_context = SYSTEM_PROMPT + f"\n\n{context}"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        system_instruction=system_with_context,
    )

    history = _build_gemini_history(conversation_history or [])
    chat = model.start_chat(history=history)
    response = chat.send_message(question)
    return response.text


def stream_explain(
    question: str,
    report,
    api_key: str,
    conversation_history: Optional[list] = None,
):
    """
    Stream the Gemini response token-by-token.
    Returns a generator that yields text chunks.
    Use with st.write_stream() for live output.
    """
    context = _build_context(report)
    system_with_context = SYSTEM_PROMPT + f"\n\n{context}"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        system_instruction=system_with_context,
    )

    history = _build_gemini_history(conversation_history or [])
    chat = model.start_chat(history=history)
    response = chat.send_message(question, stream=True)

    for chunk in response:
        if chunk.text:
            yield chunk.text


# Quick-fire preset questions
PRESET_QUESTIONS = [
    "Summarize the key bias issues in plain language for a non-technical manager.",
    "Which fairness metric is most critical here and why?",
    "What are the top 3 steps I should take before deploying this model?",
    "Explain disparate impact and the 4/5 rule in simple terms.",
    "Are the proxy features detected actually causing bias or just correlated?",
    "How do I use fairlearn to apply threshold optimization for this model?",
    "Draft an executive summary of this bias report in 150 words.",
]
