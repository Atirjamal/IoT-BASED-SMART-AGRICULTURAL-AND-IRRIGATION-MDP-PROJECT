import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set page to wide mode
st.set_page_config(layout="wide")

# CSS for background and styling
page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1530836369250-ef71a3f5e4bf?q=80&w=2070"); 
    background-size: cover;
    background-position: center;
}
h1, h2, h3, p, label {
    color: white !important;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
}
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    color: black !important;
    text-shadow: none;
}
.stMetric {
    border: 2px solid #2ecc71;
    padding: 15px;
    border-radius: 15px;
    background-color: rgba(255, 255, 255, 0.95);
}
div[data-testid="stAlert"] {
    background-color: rgba(0, 0, 0, 0.85) !important;
    border: 2px solid #2ecc71 !important;
}
div[data-testid="stAlert"] * {
    color: white !important;
    font-weight: bold !important;
    text-shadow: none !important;
}
div[data-testid="stWidgetLabel"] p {
    font-size: 18px !important;
    font-weight: bold !important;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# 1. Generate Data ONCE using Session State (Key changed to force a fresh 24h dataset)
if 'sensor_data_24h' not in st.session_state:
    # Anchor the start time to exactly midnight 7 days ago
    end_time = datetime.now()
    start_time = (end_time - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Use pandas to generate timestamps every 5 minutes
    timestamps = pd.date_range(start=start_time, end=end_time, freq='5min')
    num_points = len(timestamps)
    
    moisture_levels = np.random.randint(30, 70, size=num_points)
    temperature_levels = np.random.randint(22, 35, size=num_points) 
    humidity_levels = np.random.randint(40, 80, size=num_points)
    
    df = pd.DataFrame({
        'Time': timestamps,
        'Soil Moisture (%)': moisture_levels,
        'Temperature (°C)': temperature_levels,
        'Humidity (%)': humidity_levels
    })
    df.set_index('Time', inplace=True)
    st.session_state.sensor_data_24h = df

data = st.session_state.sensor_data_24h

# 2. Build the Dashboard UI
st.title("🌱 Smart Agriculture IoT Dashboard")

m_col1, m_col2, m_col3 = st.columns(3)
latest_moisture = data['Soil Moisture (%)'].iloc[-1]
latest_temp = data['Temperature (°C)'].iloc[-1]
latest_humidity = data['Humidity (%)'].iloc[-1]

with m_col1:
    st.metric(label="💧 Soil Moisture", value=f"{latest_moisture}%")
with m_col2:
    st.metric(label="🌡️ Temperature", value=f"{latest_temp} °C")
with m_col3:
    st.metric(label="☁️ Air Humidity", value=f"{latest_humidity}%")

# 3. Control Panel & Smart Logic
st.subheader("⚙️ System Control & Status")
ctrl_col, status_col = st.columns([1, 2])

with ctrl_col:
    manual_override = st.toggle("Enable Manual Override")
    if manual_override:
        pump_switch = st.toggle("Turn Pump ON/OFF")
    else:
        st.write("System running in **AUTO** mode.")

with status_col:
    if manual_override:
        if pump_switch:
            st.warning("⚠️ Pump Status: ON (MANUAL OVERRIDE ACTIVE)")
        else:
            st.info("ℹ️ Pump Status: OFF (MANUAL OVERRIDE ACTIVE)")
    else:
        if latest_moisture < 40 and latest_temp > 30:
            st.error("🚨 Pump Status: ON (AUTO: Soil dry & air hot. High volume.)")
        elif latest_moisture < 40:
            st.warning("⚠️ Pump Status: ON (AUTO: Standard watering mode.)")
        else:
            st.success("✅ Pump Status: OFF (AUTO: Optimal conditions met.)")

# 4. Historical Data Explorer
st.subheader("📅 Historical Data Explorer")

available_dates = data.index.date
min_date = available_dates.min()
max_date = available_dates.max()

selected_date = st.date_input("Select a date to view hourly records", max_date, min_value=min_date, max_value=max_date)

filtered_data = data[data.index.date == selected_date]

# Aggregate the 5-minute data into hourly averages
hourly_data = filtered_data.resample('1h').mean().dropna()

c1, c2 = st.columns(2)
with c1:
    st.write(f"Hourly Soil Moisture for {selected_date}")
    st.line_chart(hourly_data['Soil Moisture (%)'], color="#2ecc71")
with c2:
    st.write(f"Hourly Environment for {selected_date}")
    st.line_chart(hourly_data[['Temperature (°C)', 'Humidity (%)']])