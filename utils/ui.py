"""utils/ui.py — shared styles, nav bar, and helpers"""
import streamlit as st

# ── Color tokens ──────────────────────────────────────────────────────────────
PRIMARY   = "#6C5CE7"
SURFACE   = "#12121A"
BG        = "#0A0A0F"
CARD      = "#16161F"
BORDER    = "#2A2A3A"
TEXT      = "#F0EEF8"
MUTED     = "#8888AA"
OK        = "#00D4A0"
WARN      = "#FFB547"
DANGER    = "#FF4D6D"

GLOBAL_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Reset sidebar entirely ── */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarNav"],
header[data-testid="stHeader"],
footer,
#MainMenu {{ display: none !important; visibility: hidden !important; }}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {{
    background: {BG} !important;
    color: {TEXT};
    font-family: 'DM Sans', sans-serif;
}}
[data-testid="stMain"] {{
    background: {BG} !important;
}}
[data-testid="block-container"] {{
    background: {BG} !important;
    padding: 2.5rem 3rem !important;
    max-width: 1100px !important;
    margin: 0 auto !important;
}}

/* ── Top nav ── */
.fl-nav {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 0 1.2rem;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 2rem;
}}
.fl-logo {{
    font-family: 'Syne', sans-serif;
    font-size: 1.35rem; font-weight: 800;
    color: {TEXT}; letter-spacing: -.02em;
}}
.fl-logo span {{ color: {PRIMARY}; }}
.fl-nav-links {{ display: flex; gap: 6px; }}
.fl-nav-btn {{
    background: transparent; border: 1px solid {BORDER};
    color: {MUTED}; padding: 6px 14px; border-radius: 8px;
    font-size: .82rem; cursor: pointer; font-family: 'DM Sans', sans-serif;
    transition: all .15s;
}}
.fl-nav-btn:hover {{ border-color: {PRIMARY}; color: {TEXT}; }}
.fl-nav-btn.active {{ background: {PRIMARY}22; border-color: {PRIMARY}; color: {TEXT}; }}

/* ── Page title ── */
.fl-page-title {{
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem; font-weight: 700;
    letter-spacing: -.03em; color: {TEXT};
    margin: 0 0 .3rem;
}}
.fl-page-sub {{
    font-size: .93rem; color: {MUTED}; margin: 0 0 2rem;
}}

/* ── Cards ── */
.fl-card {{
    background: {CARD}; border: 1px solid {BORDER};
    border-radius: 16px; padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}}

/* ── Metric chips ── */
.fl-metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px,1fr)); gap: 12px; margin-bottom: 1.5rem; }}
.fl-metric {{
    background: {CARD}; border: 1px solid {BORDER};
    border-radius: 12px; padding: 1rem 1.1rem;
}}
.fl-metric-label {{ font-size: .72rem; color: {MUTED}; text-transform: uppercase; letter-spacing: .07em; margin-bottom: .3rem; }}
.fl-metric-val {{ font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 700; line-height: 1; }}
.fl-metric-status {{ font-size: .75rem; margin-top: .3rem; }}
.ok  {{ color: {OK};   }} .warn {{ color: {WARN}; }} .danger {{ color: {DANGER}; }}

/* ── Flag badges ── */
.badge-high   {{ background: {DANGER}22; color: {DANGER}; border: 1px solid {DANGER}55; padding: 2px 10px; border-radius: 20px; font-size: .75rem; font-weight: 600; }}
.badge-medium {{ background: {WARN}22;   color: {WARN};   border: 1px solid {WARN}55;   padding: 2px 10px; border-radius: 20px; font-size: .75rem; font-weight: 600; }}
.badge-low    {{ background: {OK}22;     color: {OK};     border: 1px solid {OK}55;     padding: 2px 10px; border-radius: 20px; font-size: .75rem; font-weight: 600; }}

/* ── Rec cards ── */
.rec-high   {{ background: {DANGER}0D; border-left: 3px solid {DANGER}; border-radius: 10px; padding: .9rem 1.1rem; margin: .5rem 0; }}
.rec-medium {{ background: {WARN}0D;   border-left: 3px solid {WARN};   border-radius: 10px; padding: .9rem 1.1rem; margin: .5rem 0; }}
.rec-low    {{ background: {OK}0D;     border-left: 3px solid {OK};     border-radius: 10px; padding: .9rem 1.1rem; margin: .5rem 0; }}

/* ── Progress bars ── */
.fl-bar-wrap {{ background: {BORDER}; border-radius: 4px; height: 7px; overflow: hidden; margin: 4px 0 10px; }}
.fl-bar-fill {{ height: 100%; border-radius: 4px; transition: width .6s ease; }}

/* ── Buttons ── */
.stButton > button {{
    background: {PRIMARY} !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important;
    padding: .55rem 1.4rem !important;
}}
.stButton > button:hover {{ opacity: .88 !important; }}

/* ── Inputs ── */
.stTextInput input, .stSelectbox > div > div, .stTextArea textarea {{
    background: {CARD} !important; color: {TEXT} !important;
    border: 1px solid {BORDER} !important; border-radius: 10px !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {CARD}; border-radius: 10px; border: 1px solid {BORDER}; gap: 4px; padding: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent; color: {MUTED}; border-radius: 8px;
    font-family: 'DM Sans', sans-serif; font-size: .88rem;
}}
.stTabs [aria-selected="true"] {{
    background: {PRIMARY}33 !important; color: {TEXT} !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; }}

/* ── Chat ── */
[data-testid="stChatMessage"] {{ background: {CARD} !important; border-radius: 14px !important; border: 1px solid {BORDER} !important; }}

/* ── Expander ── */
.streamlit-expanderHeader {{ background: {CARD} !important; border-radius: 10px !important; }}

/* ── Section header ── */
.fl-section {{
    font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 600;
    color: {TEXT}; border-bottom: 1px solid {BORDER};
    padding-bottom: .4rem; margin: 1.5rem 0 1rem;
}}

/* ── Divider ── */
hr {{ border-color: {BORDER} !important; }}

/* ── Streamlit alerts ── */
.stAlert {{ border-radius: 12px !important; }}
</style>
"""

NAV_PAGES = [
    ("🏠", "Home",            "home"),
    ("📂", "Upload",          "upload"),
    ("📊", "Metrics",         "metrics"),
    ("👥", "Groups",          "groups"),
    ("🚩", "Flags",           "flags"),
    ("💡", "Recommendations", "recommendations"),
    ("🤖", "AI Explainer",    "ai_explainer"),
]


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def nav_bar(current: str):
    """Render the top navigation bar with clickable page buttons."""
    inject_css()
    done = st.session_state.get("analysis_done", False)

    links_html = ""
    for icon, label, key in NAV_PAGES:
        active_cls = "active" if key == current else ""
        # Lock pages that need data
        locked = key in ("metrics","groups","flags","recommendations","ai_explainer") and not done
        if locked:
            links_html += f'<span class="fl-nav-btn" style="opacity:.35;cursor:not-allowed">{icon} {label}</span>'
        else:
            links_html += f'<span class="fl-nav-btn {active_cls}" id="nav-{key}">{icon} {label}</span>'

    st.markdown(f"""
    <div class="fl-nav">
        <div class="fl-logo">Fair<span>Lens</span></div>
        <div class="fl-nav-links">{links_html}</div>
    </div>""", unsafe_allow_html=True)

    # Render invisible Streamlit buttons mapped to each nav item
    cols = st.columns(len(NAV_PAGES))
    for i, (icon, label, key) in enumerate(NAV_PAGES):
        locked = key in ("metrics","groups","flags","recommendations","ai_explainer") and not done
        with cols[i]:
            if not locked:
                if st.button(f"{icon}", key=f"__nav_{key}", help=label, use_container_width=True):
                    st.session_state.page = key
                    st.rerun()

    st.markdown('<style>.fl-nav-hidden button { opacity:0 !important; height:0 !important; overflow:hidden !important; position:absolute !important; pointer-events:none !important; }</style>', unsafe_allow_html=True)
    # Wrap nav columns in a hidden container via JS
    st.markdown("""<script>
    (function(){
      var btns = document.querySelectorAll('[data-testid="stButton"] button');
      btns.forEach(function(b){
        if(b.textContent && b.textContent.trim().length <= 2){
          var p = b.closest('[data-testid="stButton"]');
          if(p) p.style.cssText = 'opacity:0;height:0;overflow:hidden;position:absolute;pointer-events:none';
        }
      });
    })();
    </script>""", unsafe_allow_html=True)


def go(page: str):
    st.session_state.page = page
    st.rerun()


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="fl-page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="fl-page-sub">{subtitle}</div>', unsafe_allow_html=True)


def require_analysis():
    """Show a gate if no analysis has been run yet."""
    if not st.session_state.get("analysis_done", False):
        st.markdown('<div class="fl-page-title">No analysis loaded</div>', unsafe_allow_html=True)
        st.markdown('<div class="fl-page-sub">Run an analysis first to view this page.</div>', unsafe_allow_html=True)
        if st.button("Go to Upload →"):
            go("upload")
        return False
    return True
