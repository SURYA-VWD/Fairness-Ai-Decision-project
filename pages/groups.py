"""pages/groups.py"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.ui import nav_bar, page_header, require_analysis, go, MUTED


def render():
    nav_bar("groups")
    if not require_analysis(): return
    page_header("Group Analysis", "Per-demographic breakdown of fairness metrics and disparities.")

    report    = st.session_state.report
    threshold = st.session_state.get("threshold", 0.80)
    sens      = st.session_state.get("sensitive_col", "sensitive attribute")

    st.caption(f"Sensitive attribute: **{sens}**")

    from utils.charts import group_outcome_bar, group_metric_bars, disparate_impact_waterfall, proxy_feature_chart

    tab1, tab2, tab3, tab4 = st.tabs(["Outcome Rates", "Multi-Metric", "Disparate Impact", "Proxy Features"])

    with tab1:
        st.plotly_chart(group_outcome_bar(report.group_stats, threshold), use_container_width=True)

    with tab2:
        st.plotly_chart(group_metric_bars(report.group_stats), use_container_width=True)

    with tab3:
        st.plotly_chart(disparate_impact_waterfall(report.group_stats), use_container_width=True)

    with tab4:
        if report.proxy_features:
            fig = proxy_feature_chart(report.proxy_features)
            if fig: st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No significant proxy features detected.")

    st.markdown('<div class="fl-section">Group Statistics</div>', unsafe_allow_html=True)
    rows = [{"Group": g.name, "N": g.n, "Positive Rate": round(g.positive_rate,3),
             "TPR": round(g.tpr,3), "FPR": round(g.fpr,3), "FNR": round(g.fnr,3),
             "Precision": round(g.precision,3), "F1": round(g.f1,3)}
            for g in report.group_stats]
    st.dataframe(
        pd.DataFrame(rows).set_index("Group")
          .style.background_gradient(cmap="RdYlGn", subset=["Positive Rate","TPR","Precision","F1"])
                .background_gradient(cmap="RdYlGn_r", subset=["FPR","FNR"]),
        use_container_width=True,
    )

    st.markdown("<br>")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Metrics"): go("metrics")
    with c2:
        if st.button("🚩 View Flags →"): go("flags")
