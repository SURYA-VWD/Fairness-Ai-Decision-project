"""app.py — FairLens v2: no sidebar, card-based navigation"""
import streamlit as st

st.set_page_config(
    page_title="FairLens — Bias Detection",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Default page
if "page" not in st.session_state:
    st.session_state.page = "home"

page = st.session_state.page

if page == "home":
    from pages import home; home.render()
elif page == "upload":
    from pages import upload; upload.render()
elif page == "metrics":
    from pages import metrics; metrics.render()
elif page == "groups":
    from pages import groups; groups.render()
elif page == "flags":
    from pages import flags; flags.render()
elif page == "recommendations":
    from pages import recommendations; recommendations.render()
elif page == "ai_explainer":
    from pages import ai_explainer; ai_explainer.render()
else:
    st.session_state.page = "home"
    st.rerun()
