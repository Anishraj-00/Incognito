import streamlit as st

def render_kpi_cards(analytics_data, segment_data):
    """
    Renders high-level KPI cards for the dashboard.
    """
    st.markdown("### System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Monitored Locations", 
            value=segment_data.get("total_segments", 0)
        )
        
    with col2:
        avg_vol = round(analytics_data.get("global_average_volume", 0), 1)
        st.metric(
            label="Global Avg Volume (veh/hr)", 
            value=f"{avg_vol}"
        )
        
    with col3:
        high_cong = segment_data.get("high_congestion_count", 0)
        st.metric(
            label="High Congestion Zones", 
            value=high_cong,
            delta="-1" if high_cong < 2 else f"+{high_cong}",
            delta_color="inverse"
        )
        
    with col4:
        most_congested = analytics_data.get("most_congested_location", "N/A")
        st.metric(
            label="Most Congested", 
            value=most_congested
        )

    st.markdown("---")
