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

# 1. Generate Historical Data
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

# 2. Generate Weather Forecast Data
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

latest_moisture = data['Soil Moisture (%)'].iloc[-1]
latest_temp = data['Temperature (°C)'].iloc[-1]
latest_humidity = data['Humidity (%)'].iloc[-1]
today_rain_prob = weather_data['Rain Prob (%)'].iloc[0]

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("🎛️ Dashboard Menu")
menu_selection = st.sidebar.radio(
    "Select an Option:",
    ("Live Soil Status", "Historical Data", "Manual Override", "Weather Forecast", "🤖 AI Agri-Assistant")
)

st.sidebar.markdown("---")
st.sidebar.write("**System Info**")
st.sidebar.write("🟢 Cloud Connection: Active")
st.sidebar.write("📡 ESP32 Gateway: Online")

# ==========================================
# PAGE 1-4: EXISTING MODULES
# ==========================================
if menu_selection == "Live Soil Status":
    st.title("💧 Current Soil & Environment Status")
    
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric(label="💧 Soil Moisture", value=f"{latest_moisture}%")
    with m_col2:
        st.metric(label="🌡️ Temperature", value=f"{latest_temp} °C")
    with m_col3:
        st.metric(label="☁️ Air Humidity", value=f"{latest_humidity}%")

    st.subheader("Automated Pump Logic Status")
    if today_rain_prob > 75 and latest_moisture < 40:
        st.info(f"🌧️ Rain expected today ({today_rain_prob}% chance). Auto-irrigation suspended to conserve water.")
    elif latest_moisture < 40 and latest_temp > 30:
        st.error("🚨 Pump Status: ON (Soil dry & air hot. High volume needed.)")
    elif latest_moisture < 40:
        st.warning("⚠️ Pump Status: ON (Standard watering mode active.)")
    else:
        st.success("✅ Pump Status: OFF (Optimal conditions met.)")

    st.subheader("Today's Live Trends")
    today_date = datetime.now().date()
    today_data = data[data.index.date == today_date]
    
    c1, c2 = st.columns(2)
    with c1:
        st.line_chart(today_data['Soil Moisture (%)'], color="#2ecc71")
    with c2:
        st.line_chart(today_data[['Temperature (°C)', 'Humidity (%)']])

elif menu_selection == "Historical Data":
    st.title("📅 Historical Data Explorer")
    st.write("Select a previous date to view hourly aggregated sensor data.")
    
    available_dates = data.index.date
    min_date = available_dates.min()
    max_date = available_dates.max()

    selected_date = st.date_input("Choose a Date:", max_date, min_value=min_date, max_value=max_date)

    filtered_data = data[data.index.date == selected_date]
    hourly_data = filtered_data.resample('1h').mean().dropna()

    c1, c2 = st.columns(2)
    with c1:
        st.line_chart(hourly_data['Soil Moisture (%)'], color="#2ecc71")
    with c2:
        st.line_chart(hourly_data[['Temperature (°C)', 'Humidity (%)']])

elif menu_selection == "Manual Override":
    st.title("⚙️ Manual Hardware Control")
    manual_override = st.toggle("🔓 Enable Manual Override")
    
    if manual_override:
        pump_switch = st.toggle("⚡ Turn Pump ON/OFF")
        if pump_switch:
            st.warning("⚠️ COMMAND SENT: Pump is manually forced ON.")
        else:
            st.success("✅ COMMAND SENT: Pump is manually forced OFF.")
    else:
        st.write("🔒 Override disabled. System is currently running its standard automated algorithms.")

elif menu_selection == "Weather Forecast":
    st.title("🌤️ 7-Day Weather Forecast Outlook")
    cols = st.columns(7)
    for i, col in enumerate(cols):
        row = weather_data.iloc[i]
        day_str = "Today" if i == 0 else row['Date'].strftime('%a, %b %d')
        with col:
            st.markdown(f"""
            <div class="weather-card">
                <h4>{day_str}</h4>
                <p><strong>{row['Condition']}</strong></p>
                <p>🌡️ {row['Max Temp (°C)']}° / {row['Min Temp (°C)']}°</p>
                <p>🌧️ Rain: {row['Rain Prob (%)']}%</p>
            </div>
            """, unsafe_allow_html=True)
    st.line_chart(weather_data.set_index('Date')[['Max Temp (°C)', 'Rain Prob (%)']])

# ==========================================
# PAGE 5: LIVE AI AGRI-ASSISTANT (GEMINI)
# ==========================================
elif menu_selection == "🤖 AI Agri-Assistant":
    st.title("🤖 Smart Agri-Assistant (Live AI)")
    st.write("I am powered by a real Large Language Model. Ask me anything!")

    # Securely load the API key from Streamlit Secrets and strip hidden spaces
    try:
        import google.generativeai as genai
        api_key = st.secrets["GEMINI_API_KEY"].strip()
        genai.configure(api_key=api_key)
        
        # Upgraded to a newer model version
        model = genai.GenerativeModel('gemini-3.8-flash')
    except Exception as e:
        st.error(f"🚨 Initialization Error: {e}")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your live AI Agri-Assistant. How can I help you optimize your farm today?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about crops, weather, or government schemes..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Inject real-time dashboard data into the AI's brain behind the scenes
        context_prompt = f"""
        You are an expert agricultural AI assistant helping a farmer. 
        The current farm data is: Soil Moisture = {latest_moisture}%, Temperature = {latest_temp}°C, Rain Probability = {today_rain_prob}%.
        The farmer is asking: {prompt}
        Answer concisely and professionally, taking the current farm data into account if relevant.
        """

        with st.chat_message("assistant"):
            try:
                response = model.generate_content(context_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                # Exposing the exact error so we know exactly what is failing!
                st.error(f"Failed to connect to AI. Exact Error: {e}")