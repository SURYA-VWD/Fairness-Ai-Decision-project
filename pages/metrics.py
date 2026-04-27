"""pages/metrics.py"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.ui import nav_bar, page_header, require_analysis, go, OK, WARN, DANGER, PRIMARY, MUTED, TEXT, CARD, BORDER


def render():
    nav_bar("metrics")
    if not require_analysis(): return
    page_header("Fairness Metrics", "All five fairness metrics computed on your dataset.")

    report    = st.session_state.report
    threshold = st.session_state.get("threshold", 0.80)

    from utils.charts import radar_chart, bias_score_gauge
    c1, c2 = st.columns([1, 2])
    with c1:
        st.plotly_chart(bias_score_gauge(report.bias_score), use_container_width=True)
        score = report.bias_score
        level = "Low Risk" if score >= 80 else ("Moderate Risk" if score >= 55 else "High Risk")
        color = OK if score >= 80 else (WARN if score >= 55 else DANGER)
        st.markdown(f'<div style="text-align:center;font-size:.95rem;font-weight:600;color:{color}">{level}</div>', unsafe_allow_html=True)
    with c2:
        st.plotly_chart(radar_chart(report, threshold), use_container_width=True)

    st.markdown('<div class="fl-section">Metric Breakdown</div>', unsafe_allow_html=True)

    metrics = [
        ("Demographic Parity Ratio", report.demographic_parity_ratio, threshold, True,
         "Ratio of min-to-max group selection rates. ≥ threshold passes."),
        ("Disparate Impact Ratio",   report.disparate_impact_ratio,   0.80,      True,
         "EEOC 4/5 rule. Protected group rate ÷ majority rate. ≥ 0.80 required."),
        ("Equal Opportunity Diff",   abs(report.equal_opportunity_diff), 1-threshold, False,
         "Absolute TPR difference across groups. Lower is fairer."),
        ("Equalized Odds Diff",      abs(report.equalized_odds_diff),    1-threshold, False,
         "Max of TPR/FPR differences. Lower is fairer."),
        ("Overall Accuracy",         report.overall_accuracy,          0.70,      True,
         "Model accuracy on the held-out test set."),
        ("Overall F1 Score",         report.overall_f1,                0.65,      True,
         "Weighted F1 on the test set."),
    ]

    col_grid = st.columns(3)
    for i, (label, val, thr, higher_is_better, definition) in enumerate(metrics):
        passes = (val >= thr) if higher_is_better else (val <= thr)
        color  = OK if passes else DANGER
        badge  = "✓ Pass" if passes else "✗ Fail"
        with col_grid[i % 3]:
            st.markdown(f"""
            <div style="background:{CARD}; border:1px solid {color}55; border-radius:14px;
                 padding:1.1rem 1.2rem; margin-bottom:.75rem;">
                <div style="font-size:.72rem; color:{MUTED}; text-transform:uppercase;
                     letter-spacing:.07em; margin-bottom:.3rem">{label}</div>
                <div style="font-family:'Syne',sans-serif; font-size:1.9rem; font-weight:700;
                     color:{color}">{val:.3f}</div>
                <div style="font-size:.75rem; color:{color}; font-weight:600; margin-top:.2rem">
                    {badge} &nbsp;·&nbsp; threshold {thr}
                </div>
            </div>""", unsafe_allow_html=True)
            with st.expander("ℹ️"):
                st.caption(definition)

    st.markdown('<div class="fl-section">fairlearn MetricFrame</div>', unsafe_allow_html=True)
    st.dataframe(
        report.metric_frame.by_group.style.format("{:.3f}").background_gradient(cmap="RdYlGn", axis=0),
        use_container_width=True,
    )

    st.markdown("<br>")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("← Back to Upload"): go("upload")
    with c2:
        if st.button("👥 Group Analysis →"): go("groups")
    with c3:
        if st.button("🚩 View Flags →"): go("flags")
