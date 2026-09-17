import streamlit as st
import time
import os
import sys

# Add parent directory to path so we can import utils and components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.utils.api_client import TrafficAPIClient
from frontend.components.metrics import render_kpi_cards
from frontend.components.map import render_traffic_map
from frontend.components.charts import render_prediction_chart

# Page config
st.set_page_config(
    page_title="TrafficAI Congestion Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium dark aesthetics
st.markdown("""
<style>
    .reportview-container {
        background: #0E1117;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    h1, h2, h3 {
        color: #00ffcc !important;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API Client
api_client = TrafficAPIClient()

def main():
    st.title("🚦 TrafficAI Control Center")
    st.markdown("Real-time traffic congestion monitoring and AI-powered forecasting.")
    
    # Check Backend Health
    health = api_client.get_health()
    if "offline" in health.get("status", ""):
        st.error("⚠️ Backend API is offline. Showing mock data for demonstration purposes.")
        
    with st.spinner("Fetching live traffic data..."):
        # Fetch Data
        analytics_data = api_client.get_analytics()
        segment_data = api_client.get_segments()
    
    # 1. KPIs
    render_kpi_cards(analytics_data, segment_data)
    
    # 2. Main Layout (Map + Charts)
    col_map, col_chart = st.columns([1.2, 1])
    
    with col_map:
        render_traffic_map(segment_data)
        
    with col_chart:
        # Sidebar/Controls for charts
        st.markdown("### Traffic Forecast")
        segments_list = segment_data.get("segments", [])
        if segments_list:
            location_names = {s["name"]: s["location_id"] for s in segments_list}
            selected_name = st.selectbox("Select Location to Forecast:", list(location_names.keys()))
            selected_loc_id = location_names[selected_name]
            
            with st.spinner(f"Generating AI forecast for {selected_name}..."):
                predictions_data = api_client.get_predictions(selected_loc_id, horizon=12)
                render_prediction_chart(predictions_data)
        else:
            st.warning("No locations available for forecasting.")

if __name__ == "__main__":
    main()
