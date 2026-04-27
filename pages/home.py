"""pages/home.py — Landing page with feature cards"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.ui import inject_css, go, PRIMARY, CARD, BORDER, TEXT, MUTED, OK, WARN, DANGER


def render():
    inject_css()

    # ── Hero ───────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="padding: 3.5rem 0 2rem; text-align: center;">
        <div style="display:inline-block; background:{PRIMARY}22; border:1px solid {PRIMARY}55;
             border-radius:30px; padding:6px 18px; font-size:.8rem; color:{PRIMARY};
             font-weight:600; letter-spacing:.06em; margin-bottom:1.2rem;">
            ⚖️ AI-POWERED FAIRNESS ANALYSIS
        </div>
        <h1 style="font-family:'Syne',sans-serif; font-size:3.2rem; font-weight:800;
             color:{TEXT}; letter-spacing:-.04em; margin:0 0 .6rem; line-height:1.1;">
            Detect bias in your AI.<br>
            <span style="color:{PRIMARY};">Before it causes harm.</span>
        </h1>
        <p style="font-size:1.05rem; color:{MUTED}; max-width:560px; margin:0 auto 2rem; line-height:1.7;">
            Upload any dataset or ML model. FairLens automatically computes fairness metrics,
            flags disparities, and gives you actionable fixes — powered by Claude AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── CTA ────────────────────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns([2, 1.4, 2])
    with col_b:
        if st.button("🚀  Start Analysis", use_container_width=True):
            go("upload")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── How it works ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <span style="font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:700; color:{TEXT}">
            How it works
        </span>
    </div>""", unsafe_allow_html=True)

    steps = [
        ("01", "Upload", "Drop a CSV or pick a sample dataset — hiring, loans, or recidivism."),
        ("02", "Configure", "Choose your target column and the sensitive attribute (gender, race, age…)."),
        ("03", "Analyze", "FairLens trains a model and computes 5 fairness metrics via fairlearn."),
        ("04", "Review", "Explore per-group charts, proxy feature detection, and a bias score."),
        ("05", "Fix", "Get prioritized code-ready fixes. Ask Claude AI anything about the results."),
    ]

    cols = st.columns(len(steps))
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div style="background:{CARD}; border:1px solid {BORDER}; border-radius:14px;
                 padding:1.2rem 1rem; text-align:center; height:100%;">
                <div style="font-family:'Syne',sans-serif; font-size:1.6rem; font-weight:800;
                     color:{PRIMARY}; margin-bottom:.4rem;">{num}</div>
                <div style="font-family:'Syne',sans-serif; font-size:.95rem; font-weight:600;
                     color:{TEXT}; margin-bottom:.5rem;">{title}</div>
                <div style="font-size:.8rem; color:{MUTED}; line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Feature cards ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <span style="font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:700; color:{TEXT}">
            What you get
        </span>
    </div>""", unsafe_allow_html=True)

    features = [
        ("📊", "5 Fairness Metrics", OK,
         "Demographic parity, disparate impact (4/5 rule), equalized odds, equal opportunity, and predictive parity — all computed automatically."),
        ("🔍", "Proxy Detection", WARN,
         "Catches features that secretly encode demographic info (e.g. 'career gap years' encoding gender) before they sneak into your model."),
        ("🚩", "Severity Flags", DANGER,
         "Every issue is categorized High / Medium / Low with plain-English explanations of what went wrong and why it matters legally."),
        ("💡", "Code-Ready Fixes", PRIMARY,
         "fairlearn ThresholdOptimizer, SMOTE resampling, ExponentiatedGradient constraints — complete Python snippets for every recommendation."),
        ("🤖", "Gemini AI Chat", "#a29bfe",
         "Ask anything: 'Explain this to my manager', 'Which metric is most critical?', 'Write a remediation plan.' Gemini has your full report as context."),
        ("📈", "Visual Reports", "#00CEC9",
         "Radar charts, group bar comparisons, disparate impact waterfall, proxy correlation heatmaps — everything visual and interactive."),
    ]

    r1 = st.columns(3)
    r2 = st.columns(3)
    for i, (icon, title, color, desc) in enumerate(features):
        col = (r1 if i < 3 else r2)[i % 3]
        with col:
            st.markdown(f"""
            <div style="background:{CARD}; border:1px solid {BORDER}; border-radius:14px;
                 padding:1.3rem 1.2rem; height:100%; margin-bottom:.75rem;">
                <div style="font-size:1.5rem; margin-bottom:.6rem;">{icon}</div>
                <div style="font-family:'Syne',sans-serif; font-size:.95rem; font-weight:700;
                     color:{color}; margin-bottom:.4rem;">{title}</div>
                <div style="font-size:.82rem; color:{MUTED}; line-height:1.6;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Sample datasets ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <span style="font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:700; color:{TEXT}">
            Try with a sample dataset
        </span>
    </div>""", unsafe_allow_html=True)

    datasets = [
        ("🏢", "Hiring",     "Gender bias", "5,000 rows",  "Female applicants disadvantaged by 20pp in hiring rate.", DANGER),
        ("🏦", "Loan Approval","Race bias",  "4,000 rows",  "Black & Hispanic applicants face a hidden probability penalty.", WARN),
        ("⚖️", "Recidivism", "Race bias",   "3,000 rows",  "COMPAS-inspired: Black defendants systematically over-scored.", PRIMARY),
    ]
    dcols = st.columns(3)
    for col, (icon, name, bias_type, size, desc, color) in zip(dcols, datasets):
        with col:
            st.markdown(f"""
            <div style="background:{CARD}; border:1px solid {color}55; border-radius:14px;
                 padding:1.3rem 1.2rem; text-align:center;">
                <div style="font-size:2rem; margin-bottom:.5rem;">{icon}</div>
                <div style="font-family:'Syne',sans-serif; font-size:1rem; font-weight:700;
                     color:{TEXT}; margin-bottom:.2rem;">{name}</div>
                <div style="display:inline-block; background:{color}22; color:{color};
                     border:1px solid {color}55; border-radius:20px; font-size:.72rem;
                     font-weight:600; padding:2px 10px; margin-bottom:.6rem;">{bias_type}</div>
                <div style="font-size:.75rem; color:{MUTED}; margin-bottom:.3rem;">{size}</div>
                <div style="font-size:.8rem; color:{MUTED}; line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>")
    col_x, col_y, col_z = st.columns([2, 1.6, 2])
    with col_y:
        if st.button("Try a sample dataset →", use_container_width=True):
            go("upload")

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; padding:2.5rem 0 1rem; color:{MUTED}; font-size:.8rem; border-top:1px solid {BORDER}; margin-top:2rem;">
        Built with Streamlit · fairlearn · scikit-learn · Google Gemini AI
    </div>""", unsafe_allow_html=True)
