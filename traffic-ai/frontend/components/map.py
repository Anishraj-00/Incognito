import streamlit as st
import folium
from streamlit.components.v1 import html

def get_color_for_congestion(level):
    if level == "LOW":
        return "green"
    elif level == "MEDIUM":
        return "orange"
    elif level == "HIGH":
        return "red"
    return "gray"

def render_traffic_map(segment_data):
    """
    Renders a Folium map with traffic markers.
    """
    st.markdown("### Live Traffic Map")
    
    segments = segment_data.get("segments", [])
    
    if not segments:
        st.warning("No location data to display on map.")
        return
        
    # Center map on the average coordinates
    avg_lat = sum(s["latitude"] for s in segments) / len(segments)
    avg_lon = sum(s["longitude"] for s in segments) / len(segments)
    
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13, tiles="cartodbdark_matter")

    for segment in segments:
        color = get_color_for_congestion(segment.get("congestion_level", "LOW"))
        
        # HTML for popup
        popup_html = f\"\"\"
        <div style="width: 200px;">
            <h4>{segment['name']}</h4>
            <b>Volume:</b> {segment['current_volume']} veh/hr<br>
            <b>Speed:</b> {segment['speed']} km/h<br>
            <b>Status:</b> <span style="color:{color}; font-weight:bold;">{segment['congestion_level']}</span>
        </div>
        \"\"\"
        
        folium.CircleMarker(
            location=[segment["latitude"], segment["longitude"]],
            radius=10,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=segment["name"],
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7
        ).add_to(m)

    # Render folium map in Streamlit via HTML
    map_html = m.get_root().render()
    st.components.v1.html(map_html, height=500)
