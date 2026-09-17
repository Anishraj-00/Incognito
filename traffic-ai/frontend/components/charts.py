import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dateutil.parser

def render_prediction_chart(predictions_data):
    """
    Renders an interactive line chart of forecasted traffic volume using Plotly.
    """
    st.markdown(f"### Traffic Forecast: {predictions_data.get('location_id', 'Unknown')}")
    
    forecasts = predictions_data.get("forecasts", [])
    if not forecasts:
        st.warning("No prediction data available for this location.")
        return
        
    df = pd.DataFrame(forecasts)
    # Parse timestamps for better x-axis rendering
    df['timestamp'] = df['timestamp'].apply(lambda x: dateutil.parser.parse(x))
    
    fig = go.Figure()

    # Add main prediction line
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['predicted_traffic'],
        mode='lines+markers',
        name='Predicted Volume',
        line=dict(color='#00ffcc', width=3),
        marker=dict(size=8, color='#00ffcc', line=dict(width=1, color='DarkSlateGrey'))
    ))
    
    # Add uncertainty shaded area
    fig.add_trace(go.Scatter(
        x=df['timestamp'].tolist() + df['timestamp'].tolist()[::-1],
        y=(df['predicted_traffic'] + df['uncertainty']).tolist() + 
          (df['predicted_traffic'] - df['uncertainty']).tolist()[::-1],
        fill='toself',
        fillcolor='rgba(0, 255, 204, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name='Uncertainty Interval'
    ))
    
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Time",
        yaxis_title="Vehicle Volume (veh/hr)",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)
