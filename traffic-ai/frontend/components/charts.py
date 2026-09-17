"""
Chart components for TrafficAI dashboard using Plotly.
Provides interactive hourly traffic trend visualization and speed gauge.
"""

import streamlit as st
import pandas as pd
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


def render_hourly_trend_chart(hourly_data: list, current_hour: int):
    """
    Renders an interactive 24-hour dual-axis chart showing predicted
    traffic volume and average speed across the day.
    """
    df = pd.DataFrame(hourly_data)

    if not HAS_PLOTLY:
        # Fallback to Streamlit's built-in charting if Plotly is not installed
        chart_data = df.set_index("time_label")[["volume", "speed"]]
        st.line_chart(chart_data)
        return

    fig = make_subplots(
        rows=1,
        cols=1,
        specs=[[{"secondary_y": True}]],
    )

    # Traffic Volume Area/Bar Chart
    fig.add_trace(
        go.Bar(
            x=df["time_label"],
            y=df["volume"],
            name="Traffic Volume (veh/h)",
            marker=dict(
                color=df["congestion_index"],
                colorscale=[
                    [0.0, "#10B981"],
                    [0.4, "#F59E0B"],
                    [0.7, "#EF4444"],
                    [1.0, "#991B1B"],
                ],
                showscale=False,
                opacity=0.75,
            ),
            hovertemplate="<b>%{x}</b><br>Volume: %{y:,} veh/hr<extra></extra>",
        ),
        secondary_y=False,
    )

    # Average Speed Line Chart
    fig.add_trace(
        go.Scatter(
            x=df["time_label"],
            y=df["speed"],
            name="Average Speed (km/h)",
            mode="lines+markers",
            line=dict(color="#2563EB", width=3),
            marker=dict(size=6, color="#1D4ED8"),
            hovertemplate="<b>%{x}</b><br>Avg Speed: %{y:.1f} km/h<extra></extra>",
        ),
        secondary_y=True,
    )

    # Highlight currently selected prediction hour safely
    selected_time_label = f"{current_hour:02d}:00"
    fig.add_shape(
        type="line",
        x0=selected_time_label,
        x1=selected_time_label,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="#7C3AED", width=2, dash="dash"),
    )
    fig.add_annotation(
        x=selected_time_label,
        y=1,
        yref="paper",
        text="Target Time",
        showarrow=False,
        font=dict(size=11, color="#7C3AED"),
        xanchor="left",
    )

    fig.update_layout(
        title=dict(
            text="<b>24-Hour Traffic Congestion & Speed Profile</b>",
            font=dict(size=15, color="#0F172A"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        height=320,
        plot_bgcolor="#F8FAFC",
        paper_bgcolor="white",
        hovermode="x unified",
    )

    fig.update_xaxes(
        title_text="Hour of Day",
        tickangle=-45,
        gridcolor="#E2E8F0",
        tickfont=dict(size=10),
    )
    fig.update_yaxes(
        title_text="Predicted Volume (veh/hr)",
        secondary_y=False,
        gridcolor="#E2E8F0",
    )
    fig.update_yaxes(
        title_text="Average Speed (km/h)",
        secondary_y=True,
        gridcolor="rgba(0,0,0,0)",
        range=[0, 80],
    )

    st.plotly_chart(fig, use_container_width=True)


def render_speed_gauge(speed: float, free_flow: float):
    """
    Renders a gauge / speedometer visual comparing the predicted speed
    against the corridor's free-flow baseline speed.
    """
    if not HAS_PLOTLY:
        st.metric(label="Flow Velocity", value=f"{speed:.1f} km/h", delta=f"{speed - free_flow:.1f} km/h")
        return

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=speed,
            domain={"x": [0, 1], "y": [0, 1]},
            title={
                "text": "<b>Flow Velocity Gauge</b><br><span style='font-size:0.75em;color:#64748B'>Current vs Design Speed</span>",
                "font": {"size": 14, "color": "#0F172A"},
            },
            delta={
                "reference": free_flow,
                "increasing": {"color": "#10B981"},
                "decreasing": {"color": "#EF4444"},
                "suffix": " km/h",
            },
            number={"suffix": " km/h", "font": {"size": 26, "color": "#0F172A"}},
            gauge={
                "axis": {"range": [0, max(80, free_flow + 15)], "tickwidth": 1, "tickcolor": "#94A3B8"},
                "bar": {"color": "#2563EB", "thickness": 0.28},
                "bgcolor": "#F1F5F9",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, free_flow * 0.45], "color": "#FEE2E2"},
                    {"range": [free_flow * 0.45, free_flow * 0.75], "color": "#FEF3C7"},
                    {"range": [free_flow * 0.75, max(80, free_flow + 15)], "color": "#D1FAE5"},
                ],
                "threshold": {
                    "line": {"color": "#6366F1", "width": 3},
                    "thickness": 0.8,
                    "value": free_flow,
                },
            },
        )
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=260,
        paper_bgcolor="white",
    )

    st.plotly_chart(fig, use_container_width=True)
