"""
Component for rendering key performance indicator (KPI) metric cards
in the TrafficAI dashboard.
"""

import streamlit as st


def render_metric_cards(pred: dict):
    """
    Renders modern, polished metric cards for Congestion Level,
    Congestion Probability, Average Speed, and Volume.
    """
    level = pred["congestion_level"]
    prob = pred["congestion_probability"]
    speed = pred["average_speed"]
    free_flow = pred["free_flow_speed"]
    speed_delta = pred["speed_delta"]
    volume = pred["predicted_volume"]
    capacity_pct = pred["capacity_utilization"]
    level_color = pred["level_color"]
    level_bg = pred["level_bg"]
    status_text = pred["status_text"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 18px 20px;
                border: 1px solid #E2E8F0;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
                height: 100%;
            ">
                <div style="font-size: 0.8rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                    Congestion Level
                </div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="
                        display: inline-block;
                        width: 12px;
                        height: 12px;
                        border-radius: 50%;
                        background-color: {level_color};
                        box-shadow: 0 0 8px {level_color}88;
                    "></span>
                    <span style="
                        font-size: 1.6rem;
                        font-weight: 800;
                        color: {level_color};
                        line-height: 1;
                    ">{level}</span>
                </div>
                <div style="
                    display: inline-block;
                    font-size: 0.75rem;
                    font-weight: 600;
                    color: {level_color};
                    background: {level_bg};
                    padding: 3px 8px;
                    border-radius: 6px;
                ">
                    {status_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        # Determine bar fill color based on probability
        if prob < 40:
            bar_color = "#10B981"
        elif prob < 70:
            bar_color = "#F59E0B"
        else:
            bar_color = "#EF4444"

        st.markdown(
            f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 18px 20px;
                border: 1px solid #E2E8F0;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
                height: 100%;
            ">
                <div style="font-size: 0.8rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                    Congestion Probability
                </div>
                <div style="font-size: 1.6rem; font-weight: 800; color: #0F172A; line-height: 1; margin-bottom: 10px;">
                    {prob:.1f}%
                </div>
                <div style="
                    width: 100%;
                    background: #E2E8F0;
                    border-radius: 999px;
                    height: 8px;
                    overflow: hidden;
                    margin-bottom: 6px;
                ">
                    <div style="
                        width: {min(100, max(5, prob))}%;
                        height: 100%;
                        background: {bar_color};
                        border-radius: 999px;
                    "></div>
                </div>
                <div style="font-size: 0.75rem; color: #64748B;">
                    Confidence: <strong>High ({pred['congestion_index']:.2f} CI)</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        speed_delta_text = f"{speed_delta:+.1f} km/h"
        delta_color = "#EF4444" if speed_delta < -15 else ("#F59E0B" if speed_delta < 0 else "#10B981")
        st.markdown(
            f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 18px 20px;
                border: 1px solid #E2E8F0;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
                height: 100%;
            ">
                <div style="font-size: 0.8rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                    Average Speed
                </div>
                <div style="display: flex; align-items: baseline; gap: 4px; margin-bottom: 6px;">
                    <span style="font-size: 1.6rem; font-weight: 800; color: #0F172A; line-height: 1;">
                        {speed:.1f}
                    </span>
                    <span style="font-size: 0.85rem; font-weight: 600; color: #64748B;">km/h</span>
                </div>
                <div style="font-size: 0.75rem; color: #64748B;">
                    <span style="color: {delta_color}; font-weight: 700;">{speed_delta_text}</span> vs Free Flow ({free_flow} km/h)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 18px 20px;
                border: 1px solid #E2E8F0;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
                height: 100%;
            ">
                <div style="font-size: 0.8rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                    Predicted Volume
                </div>
                <div style="display: flex; align-items: baseline; gap: 4px; margin-bottom: 6px;">
                    <span style="font-size: 1.6rem; font-weight: 800; color: #0F172A; line-height: 1;">
                        {volume:,}
                    </span>
                    <span style="font-size: 0.85rem; font-weight: 600; color: #64748B;">veh/hr</span>
                </div>
                <div style="font-size: 0.75rem; color: #64748B;">
                    Capacity Util: <strong>{capacity_pct:.1f}%</strong> ({pred['capacity']} max)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
