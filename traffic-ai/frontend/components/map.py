"""
Interactive map visualization component for TrafficAI dashboard.
Uses Folium with native Streamlit HTML embedding, with fallback support.
"""

import streamlit as st
import streamlit.components.v1 as components
from frontend.utils.api_client import LOCATIONS


def render_traffic_map(pred: dict):
    """
    Renders an interactive map centered on the selected corridor with
    traffic status pins, congestion colors, and corridor details.
    """
    selected_id = pred["location_id"]
    coords = pred["coordinates"]
    level_color = pred["level_color"]

    try:
        import folium

        # Initialize map centered on selected location in Hyderabad
        m = folium.Map(
            location=[coords["lat"], coords["lon"]],
            zoom_start=13,
            tiles="OpenStreetMap",
        )

        # Plot all monitoring locations
        for loc_id, loc in LOCATIONS.items():
            is_active = loc_id == selected_id

            if is_active:
                pin_color = "red" if pred["congestion_level"] == "HIGH" else (
                    "orange" if pred["congestion_level"] == "MEDIUM" else "green"
                )
                popup_html = f"""
                <div style="font-family: sans-serif; min-width: 170px;">
                    <b style="font-size: 13px; color: #0F172A;">{loc['name']}</b><br>
                    <span style="color: #64748B; font-size: 11px;">{loc['corridor']}</span>
                    <hr style="margin: 6px 0; border: none; border-top: 1px solid #E2E8F0;">
                    <div style="font-size: 12px;">
                        <b>Status:</b> <span style="color: {level_color}; font-weight: bold;">{pred['congestion_level']}</span><br>
                        <b>Speed:</b> {pred['average_speed']} km/h<br>
                        <b>Volume:</b> {pred['predicted_volume']} veh/h<br>
                        <b>Probability:</b> {pred['congestion_probability']}%
                    </div>
                </div>
                """
                # Pulsing circle for active segment
                folium.Circle(
                    location=[loc["lat"], loc["lon"]],
                    radius=850,
                    color=level_color,
                    weight=2,
                    fill=True,
                    fill_color=level_color,
                    fill_opacity=0.25,
                    popup=popup_html,
                ).add_to(m)

                folium.Marker(
                    location=[loc["lat"], loc["lon"]],
                    popup=popup_html,
                    tooltip=f"Selected: {loc['name']} ({pred['congestion_level']})",
                    icon=folium.Icon(color=pin_color, icon="car", prefix="fa"),
                ).add_to(m)

            else:
                # Inactive corridor nodes
                popup_html = f"""
                <div style="font-family: sans-serif;">
                    <b>{loc['name']}</b><br>
                    <span style="color: #64748B; font-size: 11px;">{loc['type']}</span><br>
                    <span style="font-size: 11px;">Free-Flow Speed: {loc['free_flow_speed']} km/h</span>
                </div>
                """
                folium.CircleMarker(
                    location=[loc["lat"], loc["lon"]],
                    radius=7,
                    color="#64748B",
                    weight=1.5,
                    fill=True,
                    fill_color="#94A3B8",
                    fill_opacity=0.6,
                    popup=popup_html,
                    tooltip=loc["name"],
                ).add_to(m)

        # Render Folium map inside Streamlit using native components HTML
        map_html = m._repr_html_()
        components.html(map_html, height=360)

    except Exception:
        # Fallback if folium is missing or encounters rendering restrictions
        _render_simple_location_card(pred)


def _render_simple_location_card(pred: dict):
    """Fallback visual representation when map rendering is restricted."""
    coords = pred["coordinates"]
    st.markdown(
        f"""
        <div style="
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 8px;">📍</div>
            <h4 style="margin: 0; color: #0F172A;">{pred['location_name']}</h4>
            <p style="color: #64748B; font-size: 0.85rem; margin: 4px 0 12px 0;">{pred['corridor']}</p>
            <div style="display: inline-block; background: white; padding: 6px 14px; border-radius: 20px; border: 1px solid #CBD5E1; font-size: 0.85rem;">
                GPS: <strong>{coords['lat']:.4f}° N, {abs(coords['lon']):.4f}° W</strong> | Status: <strong style="color: {pred['level_color']};">{pred['congestion_level']}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
