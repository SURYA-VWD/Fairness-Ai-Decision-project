"""pages/flags.py"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.ui import nav_bar, page_header, require_analysis, go, OK, WARN, DANGER, CARD, BORDER, MUTED


def render():
    nav_bar("flags")
    if not require_analysis(): return
    page_header("Flagged Issues", "Disparities detected in your model, sorted by severity.")

    report = st.session_state.report
    flags  = sorted(report.flags, key=lambda f: {"High":0,"Medium":1,"Low":2}.get(f["severity"],9))

    if not flags:
        st.markdown(f'<div style="background:{OK}11;border:1px solid {OK}44;border-radius:14px;padding:2rem;text-align:center;color:{OK}">🎉 No significant bias issues detected.</div>', unsafe_allow_html=True)
        return

    high   = sum(1 for f in flags if f["severity"]=="High")
    medium = sum(1 for f in flags if f["severity"]=="Medium")
    low    = sum(1 for f in flags if f["severity"]=="Low")

    cols = st.columns(4)
    for col, label, val, color in [
        (cols[0], "Total",  len(flags), MUTED),
        (cols[1], "🔴 High",  high,     DANGER),
        (cols[2], "🟡 Medium",medium,   WARN),
        (cols[3], "🟢 Low",  low,       OK),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:{CARD};border:1px solid {color}44;border-radius:12px;
                 padding:.9rem 1rem;text-align:center;">
                <div style="font-size:.7rem;color:{MUTED};text-transform:uppercase;letter-spacing:.06em">{label}</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:700;color:{color}">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>")
    filter_sev = st.multiselect("Filter", ["High","Medium","Low"], default=["High","Medium","Low"])
    filtered = [f for f in flags if f["severity"] in filter_sev]

    color_map = {"High": DANGER, "Medium": WARN, "Low": OK}
    card_map  = {"High": "rec-high", "Medium": "rec-medium", "Low": "rec-low"}
    badge_map = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}

    for f in filtered:
        sev = f["severity"]
        c   = color_map[sev]
        st.markdown(f"""
        <div class="{card_map[sev]}" style="margin-bottom:.6rem">
            <span class="{badge_map[sev]}">{'🔴' if sev=='High' else '🟡' if sev=='Medium' else '🟢'} {sev}</span>
            <strong style="margin-left:.6rem;color:#F0EEF8">{f['title']}</strong>
            <p style="margin:.4rem 0 0;font-size:.85rem;color:{MUTED}">{f['detail']}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Group Analysis"): go("groups")
    with c2:
        if st.button("💡 Get Recommendations →"): go("recommendations")
