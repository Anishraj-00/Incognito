"""
TrafficAI — Traffic Congestion Prediction Dashboard
Main Streamlit Application
"""

import streamlit as st
from datetime import datetime, time
import sys
import os

# Ensure the root project directory is on sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frontend.utils.api_client import LOCATIONS, get_prediction
from frontend.components.metrics import render_metric_cards
from frontend.components.charts import render_hourly_trend_chart, render_speed_gauge
from frontend.components.map import render_traffic_map


# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TrafficAI — Congestion Prediction",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern, high-contrast dashboard styling
st.markdown(
    """
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        max-width: 1280px;
    }
    
    /* Header Card */
    .dashboard-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 14px;
        padding: 24px 28px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }
    
    .dashboard-header h1 {
        font-size: 1.75rem;
        font-weight: 800;
        margin: 0;
        color: #F8FAFC;
        letter-spacing: -0.02em;
    }
    
    .dashboard-header p {
        margin: 4px 0 0 0;
        color: #94A3B8;
        font-size: 0.9rem;
    }
    
    .header-badge {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #38BDF8;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* AI Recommendation Card */
    .ai-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #6366F1;
        border-radius: 12px;
        padding: 20px 24px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.05);
    }
    
    .ai-card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1E1B4B;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
    }
    
    .ai-rec-item {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-size: 0.9rem;
        color: #334155;
        line-height: 1.5;
    }

    /* Section Headings */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 24px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Primary Button Enhancements */
    button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    
    button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 2. Sidebar: Inputs & Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="font-size: 2rem;">🚦</div>
            <div>
                <h2 style="font-size: 1.25rem; font-weight: 800; margin: 0; color: #0F172A;">TrafficAI</h2>
                <span style="font-size: 0.75rem; color: #64748B; font-weight: 600;">PREDICTION DASHBOARD</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📍 Prediction Inputs")

    # 1. Location Input
    location_options = {
        loc_id: f"{loc_info['name']} ({loc_id})"
        for loc_id, loc_info in LOCATIONS.items()
    }
    selected_location_id = st.selectbox(
        "Select Road Segment / Location",
        options=list(location_options.keys()),
        format_func=lambda x: location_options[x],
        index=0,
        help="Choose an urban corridor or expressway to evaluate traffic flow.",
    )

    # 2. Date Input
    target_date = st.date_input(
        "Target Date",
        value=datetime.now().date(),
        help="Select the date you want to predict congestion for.",
    )

    # 3. Time Input
    # Preset quick-picks
    st.markdown("<span style='font-size: 0.85rem; font-weight: 600; color: #334155;'>Target Time</span>", unsafe_allow_html=True)
    time_preset = st.radio(
        "Time Presets",
        options=["Now / Current", "Morning Rush (08:30 AM)", "Evening Rush (05:30 PM)", "Midday (01:00 PM)", "Custom"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    if time_preset == "Morning Rush (08:30 AM)":
        target_time = time(8, 30)
    elif time_preset == "Evening Rush (05:30 PM)":
        target_time = time(17, 30)
    elif time_preset == "Midday (01:00 PM)":
        target_time = time(13, 0)
    elif time_preset == "Now / Current":
        target_time = datetime.now().time()
    else:
        target_time = st.time_input("Choose Custom Time", value=datetime.now().time(), label_visibility="collapsed")

    # 4. Weather Condition (Affects ML speed & congestion multipliers)
    weather_condition = st.selectbox(
        "Atmospheric / Weather Condition",
        options=["Clear", "Light Rain", "Heavy Rain"],
        index=0,
        help="Rain reduces free-flow speed and increases braking delays.",
    )

    st.markdown("---")

    # 5. Predict Traffic Button
    predict_clicked = st.button(
        "🚦 Predict Traffic",
        type="primary",
        use_container_width=True,
    )

    st.markdown(
        """
        <div style="font-size: 0.75rem; color: #64748B; margin-top: 14px; line-height: 1.4;">
            💡 <em>Tip: Try switching between Morning/Evening rush hours and rainy conditions to see how the model adapts in real time.</em>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# 3. Fetch Prediction Data
# -----------------------------------------------------------------------------
current_inputs = {
    "location_id": selected_location_id,
    "target_date": str(target_date),
    "target_time": str(target_time),
    "weather": weather_condition,
}

# Auto-recalculate if inputs change, button clicked, or stale cache detected
stale_cache = (
    "last_prediction" in st.session_state
    and st.session_state["last_prediction"].get("coordinates", {}).get("lat", 0) > 30
)

if (
    "last_prediction" not in st.session_state
    or predict_clicked
    or st.session_state.get("last_inputs") != current_inputs
    or stale_cache
):
    with st.spinner("Analyzing corridor telemetry and running congestion model..."):
        prediction = get_prediction(
            location_id=selected_location_id,
            target_date=target_date,
            target_time=target_time,
            weather_condition=weather_condition,
        )
        st.session_state["last_prediction"] = prediction
        st.session_state["last_inputs"] = current_inputs
else:
    prediction = st.session_state["last_prediction"]


# -----------------------------------------------------------------------------
# 4. Main Panel: Header & Status
# -----------------------------------------------------------------------------
loc_details = LOCATIONS.get(prediction["location_id"], LOCATIONS["LOC_A"])

st.markdown(
    f"""
    <div class="dashboard-header">
        <div>
            <h1>{prediction['location_name']}</h1>
            <p>📍 {prediction['corridor']} &nbsp;•&nbsp; 🕒 Target: <strong>{prediction['timestamp']}</strong> ({prediction['period_desc']})</p>
        </div>
        <div class="header-badge">
            <span>●</span> Source: {prediction['source']}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 5. Key Metrics Display (Congestion Level, Probability, Speed, Volume)
# -----------------------------------------------------------------------------
render_metric_cards(prediction)

# -----------------------------------------------------------------------------
# 6. Visualizations: Interactive Map & Speedometer Gauge
# -----------------------------------------------------------------------------
st.markdown("<div class='section-title'>🗺️ Spatial Corridor & Velocity Telemetry</div>", unsafe_allow_html=True)

col_map, col_gauge = st.columns([1.7, 1.1])

with col_map:
    st.markdown(
        """
        <div style="font-size: 0.85rem; color: #475569; margin-bottom: 6px; font-weight: 500;">
            Interactive Corridor Congestion Map (Click markers for details)
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_traffic_map(prediction)

with col_gauge:
    render_speed_gauge(
        speed=prediction["average_speed"],
        free_flow=prediction["free_flow_speed"],
    )
    
    # Quick Corridor Specs Card
    st.markdown(
        f"""
        <div style="
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 0.82rem;
            color: #475569;
        ">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span>Roadway Classification:</span>
                <strong>{loc_details['type']}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span>Weather Penalty:</span>
                <strong>{weather_condition} ({'0 km/h' if weather_condition == 'Clear' else ('-5 km/h' if weather_condition == 'Light Rain' else '-12 km/h')})</strong>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>Capacity Headroom:</span>
                <strong>{loc_details['capacity'] - prediction['predicted_volume']:,} veh/hr left</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# 7. 24-Hour Forecast Profile Chart
# -----------------------------------------------------------------------------
st.markdown("<div class='section-title'>📈 24-Hour Congestion & Speed Profile</div>", unsafe_allow_html=True)
render_hourly_trend_chart(
    hourly_data=prediction["hourly_forecast"],
    current_hour=target_time.hour,
)

# -----------------------------------------------------------------------------
# 8. AI Recommendations & Explainability Card
# -----------------------------------------------------------------------------
st.markdown("<div class='section-title'>🧠 AI Traffic Recommendations & Insights</div>", unsafe_allow_html=True)

rec_html_items = "".join([
    f"<div class='ai-rec-item'>{rec}</div>"
    for rec in prediction["ai_recommendations"]
])

expl_html_items = "".join([
    f"<li style='margin-bottom: 4px;'>{expl}</li>"
    for expl in prediction["explanations"]
])

st.markdown(
    f"""
    <div class="ai-card">
        <div class="ai-card-title">
            <span>🤖</span> Intelligent Dispatch & Commute Advisory
        </div>
        <div>
            {rec_html_items}
        </div>
        <div style="margin-top: 14px; padding-top: 12px; border-top: 1px dashed #CBD5E1;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 6px;">
                Model Explainability Factors
            </div>
            <ul style="margin: 0; padding-left: 20px; font-size: 0.85rem; color: #64748B;">
                {expl_html_items}
            </ul>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
