"""
utils/charts.py
Reusable Plotly chart builders for the fairness platform.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

PALETTE = {
    "primary": "#6C5CE7",
    "ok":      "#27ae60",
    "warn":    "#f39c12",
    "danger":  "#e74c3c",
    "gray":    "#95a5a6",
    "surface": "#f8f9fa",
}

GROUP_COLORS = [
    "#6C5CE7", "#00b894", "#e17055", "#0984e3",
    "#fd79a8", "#fdcb6e", "#55efc4", "#a29bfe",
]


def _threshold_shape(value: float, threshold: float = 0.80):
    return PALETTE["ok"] if value >= threshold else PALETTE["danger"]


# ── Radar / Spider chart ───────────────────────────────────────────────────────

def radar_chart(report, threshold: float = 0.80) -> go.Figure:
    metrics = ["Demographic\nParity Ratio", "Disparate\nImpact", "Equal\nOpportunity",
               "Equalized\nOdds", "Overall\nF1 Score"]

    values = [
        report.demographic_parity_ratio,
        report.disparate_impact_ratio,
        max(0.0, 1 - abs(report.equal_opportunity_diff)),
        max(0.0, 1 - abs(report.equalized_odds_diff)),
        report.overall_f1,
    ]
    values_closed = values + [values[0]]
    labels_closed = metrics + [metrics[0]]

    fig = go.Figure()

    # Threshold ring
    fig.add_trace(go.Scatterpolar(
        r=[threshold] * (len(metrics) + 1),
        theta=labels_closed,
        mode="lines",
        line=dict(color=PALETTE["warn"], dash="dash", width=1.5),
        name=f"Threshold ({threshold})",
        hoverinfo="skip",
    ))

    # Score polygon
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill="toself",
        fillcolor="rgba(108,92,231,.18)",
        line=dict(color=PALETTE["primary"], width=2),
        name="Model scores",
        hovertemplate="%{theta}: %{r:.3f}<extra></extra>",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], tickfont_size=10),
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=40, r=40, t=40, b=60),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ── Group outcome bar chart ────────────────────────────────────────────────────

def group_outcome_bar(group_stats, threshold: float = 0.80) -> go.Figure:
    names = [g.name for g in group_stats]
    pos_rates = [g.positive_rate for g in group_stats]
    colors = [_threshold_shape(r, threshold) for r in pos_rates]

    fig = go.Figure(go.Bar(
        x=names,
        y=pos_rates,
        marker_color=colors,
        text=[f"{r*100:.1f}%" for r in pos_rates],
        textposition="outside",
        hovertemplate="%{x}: %{y:.3f}<extra></extra>",
    ))

    # Threshold line
    fig.add_hline(
        y=threshold, line_dash="dash",
        line_color=PALETTE["warn"], line_width=1.5,
        annotation_text=f"Threshold {threshold}",
        annotation_position="top right",
    )

    fig.update_layout(
        xaxis_title="Group",
        yaxis_title="Positive outcome rate",
        yaxis=dict(range=[0, 1.15], tickformat=".0%"),
        showlegend=False,
        height=340,
        margin=dict(l=40, r=20, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ── Grouped metric bar chart ───────────────────────────────────────────────────

def group_metric_bars(group_stats) -> go.Figure:
    names = [g.name for g in group_stats]

    fig = go.Figure()
    metrics = [
        ("Positive rate", [g.positive_rate for g in group_stats], GROUP_COLORS[0]),
        ("TPR",           [g.tpr for g in group_stats],           GROUP_COLORS[1]),
        ("FPR",           [g.fpr for g in group_stats],           GROUP_COLORS[2]),
        ("Precision",     [g.precision for g in group_stats],     GROUP_COLORS[3]),
    ]
    for label, vals, color in metrics:
        fig.add_trace(go.Bar(
            name=label, x=names, y=vals,
            marker_color=color,
            hovertemplate=f"{label} — %{{x}}: %{{y:.3f}}<extra></extra>",
        ))

    fig.update_layout(
        barmode="group",
        xaxis_title="Group",
        yaxis_title="Rate",
        yaxis=dict(range=[0, 1.15], tickformat=".0%"),
        legend=dict(orientation="h", y=1.05),
        height=360,
        margin=dict(l=40, r=20, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ── Disparate impact waterfall ────────────────────────────────────────────────

def disparate_impact_waterfall(group_stats) -> go.Figure:
    reference = max(group_stats, key=lambda g: g.positive_rate)
    ref_rate = reference.positive_rate
    names, ratios, colors = [], [], []

    for g in group_stats:
        ratio = g.positive_rate / ref_rate if ref_rate > 0 else 0
        names.append(g.name)
        ratios.append(ratio)
        colors.append(PALETTE["ok"] if ratio >= 0.80 else PALETTE["danger"])

    fig = go.Figure(go.Bar(
        x=names, y=ratios,
        marker_color=colors,
        text=[f"{r:.2f}" for r in ratios],
        textposition="outside",
    ))
    fig.add_hline(y=0.80, line_dash="dash", line_color=PALETTE["warn"], line_width=1.5,
                  annotation_text="4/5 rule (0.80)", annotation_position="top right")
    fig.add_hline(y=1.00, line_dash="dot", line_color=PALETTE["gray"], line_width=1,
                  annotation_text=f"Reference: {reference.name}", annotation_position="bottom right")

    fig.update_layout(
        xaxis_title="Group",
        yaxis_title="DI ratio vs reference group",
        yaxis=dict(range=[0, 1.3]),
        showlegend=False,
        height=320,
        margin=dict(l=40, r=20, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ── Proxy feature correlation bar ────────────────────────────────────────────

def proxy_feature_chart(proxy_features: list[dict]) -> go.Figure:
    if not proxy_features:
        return None
    features = [p["feature"] for p in proxy_features]
    corrs    = [p["correlation"] for p in proxy_features]
    colors   = [PALETTE["danger"] if p["risk"] == "High" else PALETTE["warn"] for p in proxy_features]

    fig = go.Figure(go.Bar(
        x=corrs, y=features,
        orientation="h",
        marker_color=colors,
        text=[f"{c:.3f}" for c in corrs],
        textposition="outside",
    ))
    fig.add_vline(x=0.60, line_dash="dash", line_color=PALETTE["danger"],
                  annotation_text="High risk (0.60)", annotation_position="top")
    fig.add_vline(x=0.35, line_dash="dot", line_color=PALETTE["warn"],
                  annotation_text="Medium risk (0.35)", annotation_position="top")

    fig.update_layout(
        xaxis_title="Absolute correlation with sensitive attribute",
        xaxis=dict(range=[0, 1]),
        yaxis_title="Feature",
        height=max(200, len(features) * 45 + 80),
        margin=dict(l=20, r=60, t=20, b=40),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ── Bias score gauge ──────────────────────────────────────────────────────────

def bias_score_gauge(score: float) -> go.Figure:
    color = (
        PALETTE["ok"]   if score >= 80 else
        PALETTE["warn"] if score >= 55 else
        PALETTE["danger"]
    )
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "/100", "font": {"size": 28, "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color, "thickness": 0.25},
            "steps": [
                {"range": [0,  55], "color": "#fde8e8"},
                {"range": [55, 80], "color": "#fef3cd"},
                {"range": [80, 100],"color": "#d4edda"},
            ],
            "threshold": {
                "line": {"color": "#2d3436", "width": 2},
                "thickness": 0.75,
                "value": score,
            },
        },
        title={"text": "Bias Score", "font": {"size": 14}},
        domain={"x": [0, 1], "y": [0, 1]},
    ))
    fig.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
