"""Plotly chart components for the dashboard."""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def _base_layout(**kwargs):
    defaults = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": dict(color="#e2e8f0", family="Inter, sans-serif"),
        "margin": dict(l=20, r=20, t=40, b=20),
    }
    defaults.update(kwargs)
    return go.Layout(**defaults)


def create_score_gauge(score: int) -> go.Figure:
    """Create a neon-styled gauge chart for the password score."""
    if score < 40:
        color = "#ef4444"
    elif score < 60:
        color = "#f59e0b"
    elif score < 75:
        color = "#eab308"
    elif score < 90:
        color = "#10b981"
    else:
        color = "#00d4ff"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Score", "font": {"size": 16, "color": "#e2e8f0"}},
        number={"font": {"size": 48, "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#475569",
                     "tickfont": {"size": 10}},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(255,255,255,0.03)",
            "borderwidth": 1,
            "bordercolor": "#1e293b",
            "steps": [
                {"range": [0, 20], "color": "rgba(239,68,68,0.1)"},
                {"range": [20, 40], "color": "rgba(249,115,22,0.1)"},
                {"range": [40, 60], "color": "rgba(245,158,11,0.1)"},
                {"range": [60, 75], "color": "rgba(234,179,8,0.1)"},
                {"range": [75, 90], "color": "rgba(16,185,129,0.1)"},
                {"range": [90, 100], "color": "rgba(0,212,255,0.1)"},
            ],
            "threshold": {
                "line": {"color": "#ffffff", "width": 2},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(_base_layout(height=250))
    return fig


def create_strength_bar(label: str, score: int) -> go.Figure:
    """Create a horizontal bar showing strength."""
    colors = {
        "Very Weak": "#ef4444",
        "Weak": "#f97316",
        "Fair": "#f59e0b",
        "Good": "#eab308",
        "Strong": "#10b981",
        "Very Strong": "#00d4ff",
    }
    color = colors.get(label, "#6b7280")

    fig = go.Figure(go.Bar(
        x=[score],
        y=["Strength"],
        orientation="h",
        marker=dict(color=color, line=dict(color=color, width=0)),
        text=[f"{label} ({score}/100)"],
        textposition="inside",
        textfont=dict(color="#ffffff", size=14, family="bold"),
        width=0.5,
    ))
    fig.update_xaxes(range=[0, 100], showgrid=False, visible=False)
    fig.update_yaxes(showgrid=False, visible=False)
    fig.update_layout(_base_layout(height=80, margin=dict(l=0, r=0, t=0, b=0)))
    return fig


def create_score_trend_chart(scores: list[int]) -> go.Figure:
    """Create a line chart showing score trends over time."""
    if not scores:
        scores = [0]
    df = pd.DataFrame({"Index": list(range(1, len(scores) + 1)), "Score": scores})

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Index"],
        y=df["Score"],
        mode="lines+markers",
        line=dict(color="#00d4ff", width=2),
        marker=dict(size=6, color="#bd00ff", line=dict(color="#ffffff", width=1)),
        fill="tozeroy",
        fillcolor="rgba(0,212,255,0.08)",
        name="Score",
    ))
    fig.update_xaxes(title="", showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(range=[0, 100], title="Score", showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    fig.update_layout(_base_layout(height=300))
    return fig


def create_strength_distribution_chart(distribution: dict) -> go.Figure:
    """Create a pie/donut chart of strength distribution."""
    if not distribution:
        distribution = {"No Data": 1}

    colors = {
        "Very Weak": "#ef4444",
        "Weak": "#f97316",
        "Fair": "#f59e0b",
        "Good": "#eab308",
        "Strong": "#10b981",
        "Very Strong": "#00d4ff",
        "No Data": "#6b7280",
    }

    labels = list(distribution.keys())
    values = list(distribution.values())
    pie_colors = [colors.get(l, "#6b7280") for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=pie_colors, line=dict(color="#0a0e1a", width=2)),
        textfont=dict(color="#e2e8f0", size=11),
        textinfo="label+percent",
    ))
    fig.update_layout(_base_layout(height=300, showlegend=False))
    return fig


def create_entropy_chart(entropy: float) -> go.Figure:
    """Create a bar chart showing entropy vs recommended levels."""
    categories = ["Your Password", "Minimum (40)", "Recommended (80)", "Excellent (128)"]
    values = [entropy, 40, 80, 128]
    colors = ["#00d4ff", "#ef4444", "#f59e0b", "#10b981"]

    fig = go.Figure(go.Bar(
        x=categories,
        y=values,
        marker=dict(color=colors),
        text=[f"{v:.0f}" for v in values],
        textposition="auto",
        textfont=dict(color="#ffffff", size=12),
    ))
    fig.update_yaxes(range=[0, 140], title="Bits", showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    fig.update_layout(_base_layout(height=250))
    return fig


def create_radar_chart(analysis: dict) -> go.Figure:
    """Create a radar chart showing multiple security dimensions."""
    categories = ["Length", "Diversity", "Entropy", "Complexity", "Uniqueness"]
    
    length_score = min(analysis.get("length", 0) / 20 * 100, 100)
    diversity_score = analysis.get("character_diversity", 0) * 100
    entropy_score = min(analysis.get("entropy_bits", 0) / 128 * 100, 100)
    complexity_score = min(analysis.get("charset_size", 0) / 95 * 100, 100)
    uniqueness_score = 0 if analysis.get("is_common_password") else 100
    if analysis.get("has_keyboard_pattern"):
        uniqueness_score -= 20
    if analysis.get("has_dictionary_word"):
        uniqueness_score -= 20
    if analysis.get("has_sequential_chars"):
        uniqueness_score -= 15
    uniqueness_score = max(0, uniqueness_score)

    values = [length_score, diversity_score, entropy_score, complexity_score, uniqueness_score]

    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(0,212,255,0.15)",
        line=dict(color="#00d4ff", width=2),
        name="Security",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 100], showgrid=True, gridcolor="rgba(255,255,255,0.1)",
                           tickfont=dict(color="#64748b", size=9)),
            angularaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)",
                            tickfont=dict(color="#e2e8f0", size=11)),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        margin=dict(l=40, r=40, t=20, b=20),
        height=300,
        showlegend=False,
    )
    return fig