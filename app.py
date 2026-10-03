import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set page to wide mode
st.set_page_config(layout="wide", page_title="Smart Agriculture Dashboard", page_icon="🌱")

# CSS for background image, metrics, and alert styling
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
/* Style for Weather Cards */
.weather-card {
    background-color: rgba(255, 255, 255, 0.92);
    border-radius: 12px;
    padding: 12px;
    text-align: center;
    border: 1px solid #2ecc71;
    margin-bottom: 10px;
}
.weather-card h4, .weather-card p {
    color: black !important;
    text-shadow: none !important;
    margin: 3px 0;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# 1. Generate Historical Data ONCE using Session State
if 'sensor_data_24h' not in st.session_state:
    end_time = datetime.now()
    start_time = (end_time - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
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

# 2. Generate 7-Day Weather Forecast Data
if 'weather_forecast' not in st.session_state:
    today = datetime.now().date()
    forecast_dates = [today + timedelta(days=i) for i in range(7)]
    conditions = ['Sunny ☀️', 'Partly Cloudy ⛅', 'Cloudy ☁️', 'Light Rain 🌧️', 'Heavy Rain ⛈️', 'Sunny ☀️', 'Clear 🌤️']
    
    weather_df = pd.DataFrame({
        'Date': forecast_dates,
        'Condition': conditions,
        'Max Temp (°C)': [33, 31, 29, 26, 25, 30, 34],
        'Min Temp (°C)': [22, 21, 20, 19, 18, 20, 23],
        'Humidity (%)': [55, 60, 68, 85, 90, 62, 50],
        'Rain Prob (%)': [10, 25, 40, 80, 95, 15, 5]
    })
    st.session_state.weather_forecast = weather_df

data = st.session_state.sensor_data_24h
weather_data = st.session_state.weather_forecast

# Dashboard Title
st.title("🌱 Smart Agriculture IoT Dashboard")

# 3. Live Sensor Metrics
m_col1, m_col2, m_col3 = st.columns(3)
latest_moisture = data['Soil Moisture (%)'].iloc[-1]
latest_temp = data['Temperature (°C)'].iloc[-1]
latest_humidity = data['Humidity (%)'].iloc[-1]

with m_col1:
    st.metric(label="💧 Soil Moisture (Live)", value=f"{latest_moisture}%")
with m_col2:
    st.metric(label="🌡️ Temperature (Live)", value=f"{latest_temp} °C")
with m_col3:
    st.metric(label="☁️ Air Humidity (Live)", value=f"{latest_humidity}%")

# 4. System Control & Smart Logic
st.subheader("⚙️ System Control & Status")
ctrl_col, status_col = st.columns([1, 2])

today_rain_prob = weather_data['Rain Prob (%)'].iloc[0]

with ctrl_col:
    manual_override = st.toggle("Enable Manual Override")
    if manual_override:
        pump_switch = st.toggle("Turn Pump ON/OFF")
    else:
        st.write("System running in **AUTO** mode.")

with status_col:
    if manual_override:
        if pump_switch:
            st.warning("⚠️️ Pump Status: ON (MANUAL OVERRIDE ACTIVE)")
        else:
            st.info("ℹ️ Pump Status: OFF (MANUAL OVERRIDE ACTIVE)")
    else:
        if today_rain_prob > 75 and latest_moisture < 40:
            st.info(f"🌧️ Rain expected today ({today_rain_prob}% chance). Auto-irrigation suspended to conserve water.")
        elif latest_moisture < 40 and latest_temp > 30:
            st.error("🚨 Pump Status: ON (AUTO: Soil dry & air hot. High volume.)")
        elif latest_moisture < 40:
            st.warning("⚠️ Pump Status: ON (AUTO: Standard watering mode.)")
        else:
            st.success("✅ Pump Status: OFF (AUTO: Optimal conditions met.)")

# 5. Weather Forecast Section (Next 1 Week)
st.subheader("🌤️ 7-Day Weather Forecast Outlook")

# Display 7 Daily Cards
cols = st.columns(7)
for i, col in enumerate(cols):
    row = weather_data.iloc[i]
    day_str = "Today" if i == 0 else row['Date'].strftime('%a, %b %d')
    with col:
        st.markdown(f"""
        <div class="weather-card">
            <h4>{day_str}</h4>
            <p><strong>{row['Condition']}</strong></p>
            <p>🌡️ {row['Max Temp (°C)']}° / {row['Min Temp (°C)']}°C</p>
            <p>💧 Hum: {row['Humidity (%)']}%</p>
            <p>🌧️ Rain: {row['Rain Prob (%)']}%</p>
        </div>
        """, unsafe_allow_html=True)

# 7-Day Temperature & Rain Trend Chart
st.write("**7-Day Expected Temperature and Rain Probability Trends**")
chart_weather = weather_data.set_index('Date')
st.line_chart(chart_weather[['Max Temp (°C)', 'Rain Prob (%)']])

# 6. Historical Data Explorer
st.subheader("📅 Historical Data Explorer")
available_dates = data.index.date
min_date = available_dates.min()
max_date = available_dates.max()

selected_date = st.date_input("Select a date to view hourly records", max_date, min_value=min_date, max_value=max_date)

filtered_data = data[data.index.date == selected_date]
hourly_data = filtered_data.resample('1h').mean().dropna()

c1, c2 = st.columns(2)
with c1:
    st.write(f"Hourly Soil Moisture for {selected_date}")
    st.line_chart(hourly_data['Soil Moisture (%)'], color="#2ecc71")
with c2:
    st.write(f"Hourly Environment for {selected_date}")
    st.line_chart(hourly_data[['Temperature (°C)', 'Humidity (%)']])