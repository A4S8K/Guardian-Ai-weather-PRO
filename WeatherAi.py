import streamlit as st
import requests
import pandas as pd
from openai import OpenAI

# =====================================================
# 1. CONFIGURATION
# =====================================================
st.set_page_config(page_title="Guardian AI Weather PRO", layout="wide", page_icon="🌍")

# API Keys from Secrets
W_API_KEY = st.secrets.get("WEATHER_API_KEY")
OA_API_KEY = st.secrets.get("OPENAI_API_KEY")

client = OpenAI(api_key=OA_API_KEY) if OA_API_KEY else None

LANGUAGES = {"Қазақша":"kk", "Русский":"ru", "English":"en"}

# =====================================================
# 2. TRANSLATIONS
# =====================================================
TRANSLATIONS = {
    "Қазақша": {
        "enter_city":"📍 Қала атын жазыңыз", "search":"Іздеу", 
        "temp":"🌡 Температура", "humidity":"💧 Ылғалдылық", 
        "wind":"🌬 Жел", "uv":"☀️ UV", "aqi":"🌪 Ауа сапасы",
        "temp_24h":"📈 24 сағаттық болжам", "forecast_7d":"📅 3 күндік болжам",
        "gpt_analysis":"🤖 AI Талдау", "map_layer":"Карта түрі",
        "windy_map":"🌍 Windy Картасы", "no_ai":"AI кілті табылмады",
        "error_fetch": "❌ Мәлімет алу мүмкін болмады. Кілтіңізді тексеріңіз."
    },
    "Русский": {
        "enter_city":"📍 Введите город", "search":"Поиск", 
        "temp":"🌡 Температура", "humidity":"💧 Влажность",
        "wind":"🌬 Ветер", "uv":"☀️ UV", "aqi":"🌪 Воздух",
        "temp_24h":"📈 Прогноз на 24 часа", "forecast_7d":"📅 Прогноз на 3 дня",
        "gpt_analysis":"🤖 AI Анализ", "map_layer":"Слой",
        "windy_map":"🌍 Карта Windy", "no_ai":"API ключ не найден",
        "error_fetch": "❌ Ошибка получения данных."
    },
    "English": {
        "enter_city":"📍 Enter city", "search":"Search", 
        "temp":"🌡 Temp", "humidity":"💧 Humidity",
        "wind":"🌬 Wind", "uv":"☀️ UV", "aqi":"🌪 AQI",
        "temp_24h":"📈 24h Forecast", "forecast_7d":"📅 3 Day Forecast",
        "gpt_analysis":"🤖 AI Analysis", "map_layer":"Layer",
        "windy_map":"🌍 Windy Map", "no_ai":"Key not found",
        "error_fetch": "❌ Connection error."
    }
}

# =====================================================
# 3. WEATHERAPI DATA FETCHING
# =====================================================
@st.cache_data(ttl=900)
def get_weather_data(city, lang_code):
    if not W_API_KEY:
        return None
    # WeatherAPI provides Current, Forecast, and Air Quality in one call
    url = f"http://api.weatherapi.com/v1/forecast.json?key={W_API_KEY}&q={city}&days=3&aqi=yes&lang={lang_code}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return None

# =====================================================
# 4. INTERFACE
# =====================================================
selected_lang = st.sidebar.selectbox("🌐 Language", list(LANGUAGES.keys()))
t = TRANSLATIONS[selected_lang]
lang_code = LANGUAGES[selected_lang]

city_query = st.sidebar.text_input(t["enter_city"])

if st.sidebar.button(t["search"]):
    if city_query:
        data = get_weather_data(city_query, lang_code)
        if data:
            st.session_state.weather_data = data
        else:
            st.sidebar.error(t["error_fetch"])

# DISPLAY RESULTS
if "weather_data" in st.session_state:
    wd = st.session_state.weather_data
    curr = wd["current"]
    loc = wd["location"]
    forecast = wd["forecast"]["forecastday"]

    st.title(f"📍 {loc['name']}, {loc['country']}")
    
    # Main Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(t["temp"], f"{curr['temp_c']}°C")
    m2.metric(t["humidity"], f"{curr['humidity']}%")
    m3.metric(t["wind"], f"{curr['wind_kph']} kph")
    m4.metric(t["uv"], curr['uv'])
    
    # US-EPA standard AQI
    aqi_val = curr["air_quality"]["us-epa-index"]
    m5.metric(t["aqi"], aqi_val)

    st.divider()

    # Layout: Chart and Forecast
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader(t["temp_24h"])
        # Extract hourly data for the current day
        hourly_data = forecast[0]["hour"]
        df_hourly = pd.DataFrame({
            "Time": [h["time"] for h in hourly_data],
            "Temp": [h["temp_c"] for h in hourly_data]
        }).set_index("Time")
        st.line_chart(df_hourly)

    with col_right:
        st.subheader(t["forecast_7d"])
        df_daily = pd.DataFrame({
            "Date": [d["date"] for d in forecast],
            "Max": [d["day"]["maxtemp_c"] for d in forecast],
            "Min": [d["day"]["mintemp_c"] for d in forecast],
            "Condition": [d["day"]["condition"]["text"] for d in forecast]
        })
        st.table(df_daily)

    # AI Analysis
    if st.button(t["gpt_analysis"]):
        if client:
            with st.spinner("..."):
                prompt = f"Analyze: {loc['name']}, {curr['temp_c']}C, {curr['condition']['text']}. Language: {selected_lang}"
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.info(res.choices[0].message.content)
        else:
            st.warning(t["no_ai"])

    # Map
    st.subheader(t["windy_map"])
    map_url = f"https://www.windy.com/embed2.html?lat={loc['lat']}&lon={loc['lon']}&zoom=7"
    st.components.v1.iframe(map_url, height=500)
    
