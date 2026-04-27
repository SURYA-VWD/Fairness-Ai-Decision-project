"""pages/recommendations.py"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.ui import nav_bar, page_header, require_analysis, go, OK, WARN, DANGER, PRIMARY, MUTED, CARD, BORDER, TEXT


def _build_recs(report, threshold):
    recs = []
    dp, di = report.demographic_parity_ratio, report.disparate_impact_ratio
    eo, eop = abs(report.equalized_odds_diff), abs(report.equal_opportunity_diff)

    if di < 0.80:
        recs.append({"priority":"High","category":"Data",
            "title":"Rebalance training data (SMOTE)",
            "detail":f"Disparate impact {di:.2f} violates the 4/5 rule. Apply SMOTE or stratified resampling to equalize positive-outcome representation.",
            "code":"from imblearn.over_sampling import SMOTE\nsm = SMOTE(random_state=42)\nX_res, y_res = sm.fit_resample(X_train, y_train)"})

    high_proxy = [p for p in report.proxy_features if p["risk"]=="High"]
    if high_proxy:
        names = ", ".join(f"'{p['feature']}'" for p in high_proxy)
        recs.append({"priority":"High","category":"Features",
            "title":f"Remove proxy features: {names}",
            "detail":f"These features correlate strongly with the sensitive attribute and encode demographic info indirectly.",
            "code":f"drop_cols = {[p['feature'] for p in high_proxy]}\nX_train = X_train.drop(columns=drop_cols)"})

    if dp < threshold:
        recs.append({"priority":"High","category":"Model",
            "title":"Apply ThresholdOptimizer (fairlearn)",
            "detail":f"Demographic parity ratio {dp:.2f} < threshold. Use group-specific thresholds without retraining.",
            "code":"from fairlearn.postprocessing import ThresholdOptimizer\nopt = ThresholdOptimizer(\n    estimator=your_model,\n    constraints='demographic_parity',\n    objective='balanced_accuracy_score',\n    predict_method='predict_proba',\n)\nopt.fit(X_train, y_train, sensitive_features=s_train)\ny_pred = opt.predict(X_test, sensitive_features=s_test)"})

    if eo > 0.10:
        recs.append({"priority":"Medium","category":"Model",
            "title":"ExponentiatedGradient with EqualizedOdds",
            "detail":f"Equalized odds diff {eo:.2f}. Add in-processing fairness constraints during training.",
            "code":"from fairlearn.reductions import ExponentiatedGradient, EqualizedOdds\nfrom sklearn.linear_model import LogisticRegression\nmitigator = ExponentiatedGradient(\n    estimator=LogisticRegression(),\n    constraints=EqualizedOdds(),\n)\nmitigator.fit(X_train, y_train, sensitive_features=s_train)"})

    total = sum(g.n for g in report.group_stats)
    small = [g for g in report.group_stats if g.n < max(100, total*0.05)]
    if small:
        names_s = ", ".join(f"'{g.name}'" for g in small)
        recs.append({"priority":"Medium","category":"Data",
            "title":f"Collect more data for: {names_s}",
            "detail":"Small sample sizes make fairness metrics unreliable. Target 500–1,000 samples per group.",
            "code":None})

    recs.append({"priority":"Low","category":"Model",
        "title":"Adversarial debiasing (AIF360)",
        "detail":"Use IBM AI Fairness 360's AdversarialDebiasing to penalize demographic-correlated predictions during training.",
        "code":"# pip install aif360\nfrom aif360.algorithms.inprocessing import AdversarialDebiasing\nimport tensorflow as tf\nsess = tf.compat.v1.Session()\ndebiaser = AdversarialDebiasing(\n    privileged_groups=[{'group': 1}],\n    unprivileged_groups=[{'group': 0}],\n    scope_name='debiased',\n    sess=sess,\n)\ndebiaser.fit(dataset_train)"})

    recs.append({"priority":"Low","category":"Process",
        "title":"Set up production fairness monitoring",
        "detail":"Track demographic parity, disparate impact, and equalized odds weekly in production. Alert when any metric drops below threshold for 3 consecutive weeks.",
        "code":None})

    return sorted(recs, key=lambda r: {"High":0,"Medium":1,"Low":2}[r["priority"]])


def render():
    nav_bar("recommendations")
    if not require_analysis(): return
    page_header("Recommendations", "Prioritized, code-ready steps to fix bias before deployment.")

    report    = st.session_state.report
    threshold = st.session_state.get("threshold", 0.80)
    recs      = _build_recs(report, threshold)

    c1, c2, c3 = st.columns(3)
    for col, pri, color in [(c1,"High",DANGER),(c2,"Medium",WARN),(c3,"Low",OK)]:
        n = sum(1 for r in recs if r["priority"]==pri)
        with col:
            st.markdown(f"""
            <div style="background:{CARD};border:1px solid {color}44;border-radius:12px;
                 padding:.9rem;text-align:center;">
                <div style="font-size:.7rem;color:{MUTED};text-transform:uppercase;letter-spacing:.06em">{'🔴' if pri=='High' else '🟡' if pri=='Medium' else '🟢'} {pri}</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.7rem;font-weight:700;color:{color}">{n}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>")
    fp = st.multiselect("Filter by priority", ["High","Medium","Low"], default=["High","Medium","Low"])
    fc = st.multiselect("Filter by category", ["Data","Features","Model","Process"], default=["Data","Features","Model","Process"])
    filtered = [r for r in recs if r["priority"] in fp and r["category"] in fc]

    color_map = {"High":DANGER,"Medium":WARN,"Low":OK}
    card_map  = {"High":"rec-high","Medium":"rec-medium","Low":"rec-low"}
    badge_map = {"High":"badge-high","Medium":"badge-medium","Low":"badge-low"}

    for r in filtered:
        pri = r["priority"]
        c   = color_map[pri]
        cat_color = {"Data":"#00CEC9","Features":"#a29bfe","Model":PRIMARY,"Process":"#fd79a8"}.get(r["category"],"#888")
        st.markdown(f"""
        <div class="{card_map[pri]}">
            <span class="{badge_map[pri]}">{'🔴' if pri=='High' else '🟡' if pri=='Medium' else '🟢'} {pri}</span>
            <span style="background:{cat_color}22;color:{cat_color};border:1px solid {cat_color}55;
                 border-radius:20px;font-size:.72rem;font-weight:600;padding:2px 10px;margin-left:.5rem">{r['category']}</span>
            <strong style="margin-left:.5rem;color:#F0EEF8">{r['title']}</strong>
            <p style="margin:.4rem 0 0;font-size:.85rem;color:{MUTED}">{r['detail']}</p>
        </div>""", unsafe_allow_html=True)
        if r.get("code"):
            with st.expander("📋 Code snippet"):
                st.code(r["code"], language="python")

    st.markdown("<br>")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← View Flags"): go("flags")
    with c2:
        if st.button("🤖 Ask AI Explainer →"): go("ai_explainer")
