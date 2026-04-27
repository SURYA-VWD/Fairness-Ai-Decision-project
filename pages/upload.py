"""pages/upload.py"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.ui import nav_bar, page_header, go, CARD, BORDER, TEXT, MUTED, PRIMARY, OK, WARN, DANGER
from utils.sample_data import SAMPLE_DATASETS
from utils.fairness_engine import compute_fairness


def render():
    nav_bar("upload")
    page_header("Upload & Analyze", "Upload your dataset or choose a sample to get started.")

    # ── Source selector ────────────────────────────────────────────────────────
    source = st.radio(
        "Data source",
        ["📁 Upload my CSV / Excel", "🎯 Use a sample dataset"],
        horizontal=True,
        label_visibility="collapsed",
    )

    df = None
    dataset_name = ""

    if source == "📁 Upload my CSV / Excel":
        # Clear any cached sample dataset when switching modes
        st.session_state.pop("_sample_df", None)
        st.session_state.pop("_sample_name", None)
        uploaded = st.file_uploader(
            "Drop your file here",
            type=["csv", "xlsx", "xls"],
            label_visibility="collapsed",
        )
        if uploaded:
            try:
                df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
                dataset_name = uploaded.name
                st.markdown(f'<div style="color:{OK};font-size:.9rem">✓ Loaded <strong>{uploaded.name}</strong> — {len(df):,} rows × {df.shape[1]} columns</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Could not read file: {e}")
    else:
        choice = st.selectbox("Dataset", list(SAMPLE_DATASETS.keys()), label_visibility="collapsed")
        info = SAMPLE_DATASETS[choice]
        st.markdown(f'<div style="color:{MUTED};font-size:.85rem;margin-bottom:.5rem">{info["description"]}</div>', unsafe_allow_html=True)
        if st.button("Generate sample"):
            with st.spinner("Generating…"):
                df = info["generator"](n=5000)
                dataset_name = choice
                st.session_state._preselect_target    = info["target"]
                st.session_state._preselect_sensitive = info["sensitive"]
                st.session_state._sample_df           = df
                st.session_state._sample_name         = choice
                st.success(f"Generated {len(df):,} rows")

        # Restore df from session state across reruns so the configure section persists
        if df is None and st.session_state.get("_sample_df") is not None:
            df = st.session_state._sample_df
            dataset_name = st.session_state.get("_sample_name", choice)

    # ── Preview ────────────────────────────────────────────────────────────────
    if df is not None:
        with st.expander("Preview data"):
            st.dataframe(df.head(30), use_container_width=True)

        st.markdown('<div class="fl-section">Configure analysis</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        all_cols = df.columns.tolist()

        with c1:
            t_default = _pick(all_cols, st.session_state.get("_preselect_target"),
                              ["hired","loan_approved","two_year_recid","label","target","outcome"])
            target_col = st.selectbox("🎯 Target column (what the model predicts)", all_cols, index=t_default)

        with c2:
            remaining = [c for c in all_cols if c != target_col]
            s_default = _pick(remaining, st.session_state.get("_preselect_sensitive"),
                              ["gender","race","ethnicity","age","sex","nationality"])
            sensitive_col = st.selectbox("🔒 Sensitive attribute (demographic feature)", remaining, index=s_default)

        c3, c4 = st.columns(2)
        with c3:
            pred_options = ["— Train a model automatically —"] + [c for c in all_cols if c not in [target_col, sensitive_col]]
            pred_sel = st.selectbox("📌 Existing prediction column (optional)", pred_options)
            prediction_col = None if pred_sel.startswith("—") else pred_sel

        with c4:
            model_type = st.selectbox("⚙️ Model", ["logistic","random_forest"],
                                      format_func=lambda x: "Logistic Regression" if x=="logistic" else "Random Forest")

        threshold = st.slider("📏 Fairness threshold", 0.60, 0.95, 0.80, 0.01,
                              help="Metrics above this are acceptable. EEOC default = 0.80")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Run Fairness Analysis", use_container_width=True):
            _run(df, target_col, sensitive_col, prediction_col, model_type, threshold, dataset_name)


def _run(df, target_col, sensitive_col, prediction_col, model_type, threshold, dataset_name):
    with st.spinner("Running analysis — computing fairness metrics…"):
        try:
            report = compute_fairness(df, target_col, sensitive_col, prediction_col, model_type, threshold)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            import traceback; st.code(traceback.format_exc())
            return

    st.session_state.report        = report
    st.session_state.df            = df
    st.session_state.target_col    = target_col
    st.session_state.sensitive_col = sensitive_col
    st.session_state.threshold     = threshold
    st.session_state.analysis_done = True
    st.session_state.dataset_name  = dataset_name
    st.session_state.n_rows        = len(df)
    st.session_state.bias_score    = report.bias_score
    st.session_state.chat_history  = []

    score  = report.bias_score
    level  = "Low Risk" if score >= 80 else ("Moderate Risk" if score >= 55 else "High Risk")
    s_col  = "ok" if score >= 80 else ("warn" if score >= 55 else "danger")

    from utils.ui import OK, WARN, DANGER, CARD, BORDER, TEXT
    color_map = {"ok": OK, "warn": WARN, "danger": DANGER}
    sc = color_map[s_col]

    st.markdown(f"""
    <div style="background:{CARD}; border:1px solid {sc}55; border-radius:16px;
         padding:1.5rem 2rem; text-align:center; margin:1rem 0;">
        <div style="font-size:.8rem; color:{sc}; font-weight:600; letter-spacing:.07em; margin-bottom:.3rem">ANALYSIS COMPLETE</div>
        <div style="font-family:'Syne',sans-serif; font-size:3rem; font-weight:800; color:{sc}; line-height:1;">{score:.0f}<span style="font-size:1.2rem;color:{sc}88">/100</span></div>
        <div style="font-size:.95rem; color:{sc}; margin-top:.2rem">{level}</div>
        <div style="font-size:.8rem; color:{TEXT}88; margin-top:.6rem">{len(report.flags)} issue(s) flagged</div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📊 View Metrics →", use_container_width=True): go("metrics")
    with c2:
        if st.button("🚩 See Flags →", use_container_width=True): go("flags")
    with c3:
        if st.button("💡 Get Fixes →", use_container_width=True): go("recommendations")


def _pick(cols, preselect, candidates):
    if preselect and preselect in cols:
        return cols.index(preselect)
    for c in candidates:
        if c in cols:
            return cols.index(c)
    return 0
