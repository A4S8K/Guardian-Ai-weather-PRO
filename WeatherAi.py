import streamlit as st
import requests
import pandas as pd
from openai import OpenAI

# =====================================================
# 1. КӨНФИГУРАЦИЯ
# =====================================================
st.set_page_config(page_title="Guardian AI Weather PRO", layout="wide", page_icon="🌍")

# OpenAI API (Secrets)
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=API_KEY)
except Exception:
    client = None

API_TIMEOUT = 15
LANGUAGES = {"Қазақша":"kk", "Русский":"ru", "English":"en"}

# =====================================================
# 2. АУДАРМАЛАР
# =====================================================
TRANSLATIONS = {
    "Қазақша": {
        "enter_city":"📍 Қала атын жазыңыз", "select_city":"🏘 Нақты жерді таңдаңыз",
        "search":"Іздеу", "temp":"🌡 Температура", "humidity":"💧 Ылғалдылық", 
        "wind":"🌬 Жел", "uv":"☀️ UV", "aqi":"🌪 Ауа сапасы (AQI)",
        "temp_24h":"📈 24 сағаттық болжам", "forecast_7d":"📅 7 күндік болжам",
        "gpt_analysis":"🤖 AI Ауа райы талдауы", "map_layer":"Карта түрі",
        "windy_map":"🌍 Windy Интерактивті картасы", "no_ai":"API кілті табылмады",
        "error_fetch": "❌ Деректерді алу мүмкін болмады. Қайта байқап көріңіз."
    },
    "Русский": {
        "enter_city":"📍 Введите название города", "select_city":"🏘 Выберите локацию",
        "search":"Поиск", "temp":"🌡 Температура", "humidity":"💧 Влажность",
        "wind":"🌬 Ветер", "uv":"☀️ UV", "aqi":"🌪 Качество воздуха (AQI)",
        "temp_24h":"📈 Прогноз на 24 часа", "forecast_7d":"📅 Прогноз на 7 дней",
        "gpt_analysis":"🤖 AI Анализ погоды", "map_layer":"Слой карты",
        "windy_map":"🌍 Интерактивная карта Windy", "no_ai":"API ключ не найден",
        "error_fetch": "❌ Не удалось получить данные. Попробуйте еще раз."
    },
    "English": {
        "enter_city":"📍 Enter city name", "select_city":"🏘 Select exact location",
        "search":"Search", "temp":"🌡 Temperature", "humidity":"💧 Humidity",
        "wind":"🌬 Wind", "uv":"☀️ UV", "aqi":"🌪 Air Quality (AQI)",
        "temp_24h":"📈 24h Forecast", "forecast_7d":"📅 7 Day Forecast",
        "gpt_analysis":"🤖 AI Weather Analysis", "map_layer":"Map Layer",
        "windy_map":"🌍 Windy Interactive Map", "no_ai":"API Key not found",
        "error_fetch": "❌ Failed to fetch data. Please try again."
    }
}

# =====================================================
# 3. API ФУНКЦИЯЛАРЫ
# =====================================================
@st.cache_data(ttl=3600)
def search_location(query, lang):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=10&language={lang}&format=json"
    try:
        res = requests.get(url, timeout=API_TIMEOUT)
        return res.json().get("results", [])
    except: return []

@st.cache_data(ttl=900)
def fetch_data(lat, lon):
    weather_url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                   f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,uv_index,pressure_msl,cloud_cover,precipitation"
                   f"&hourly=temperature_2m&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto")
    air_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
    
    try:
        w_res = requests.get(weather_url, timeout=API_TIMEOUT)
        w_res.raise_for_status()
        a_res = requests.get(air_url, timeout=API_TIMEOUT)
        a_res.raise_for_status()
        return w_res.json(), a_res.json()
    except Exception as e:
        return None, None

# =====================================================
# 4. ИНТЕРФЕЙС
# =====================================================
selected_lang = st.sidebar.selectbox("🌐 Language", list(LANGUAGES.keys()))
t = TRANSLATIONS[selected_lang]

city_input = st.sidebar.text_input(t["enter_city"])

if city_input:
    locations = search_location(city_input, LANGUAGES[selected_lang])
    if locations:
        loc_options = {f"{l.get('name')} ({l.get('admin1', '')}, {l.get('country', '')})": l for l in locations}
        selected_option = st.sidebar.selectbox(t["select_city"], list(loc_options.keys()))
        
        if st.sidebar.button(t["search"]):
            target = loc_options[selected_option]
            w_data, a_data = fetch_data(target["latitude"], target["longitude"])
            
            # ТЕКСЕРУ: Деректер бос болмаса ғана сессияға сақтаймыз
            if w_data and "current" in w_data:
                st.session_state.current_data = {"loc": target, "weather": w_data, "air": a_data}
            else:
                st.sidebar.error(t["error_fetch"])
    else:
        st.sidebar.error("❌ Nothing found")

# НӘТИЖЕНІ ШЫҒАРУ
if "current_data" in st.session_state:
    data = st.session_state.current_data
    loc = data["loc"]
    w = data["weather"]
    cur = w["current"]
    
    st.title(f"📍 {loc['name']}, {loc.get('country', '')}")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(t["temp"], f"{cur['temperature_2m']}°C")
    m2.metric(t["humidity"], f"{cur['relative_humidity_2m']}%")
    m3.metric(t["wind"], f"{cur['wind_speed_10m']} m/s")
    m4.metric(t["uv"], cur.get("uv_index", 0))
    
    aqi = data["air"]["current"]["us_aqi"] if data["air"] else "N/A"
    m5.metric(t["aqi"], aqi)

    if isinstance(aqi, (int, float)):
        if aqi <= 50: st.success("✅ Good Quality")
        elif aqi <= 100: st.warning("⚠️ Moderate Quality")
        else: st.error("🚨 Unhealthy Level")

    st.divider()

    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        st.subheader(t["temp_24h"])
        df_24h = pd.DataFrame({
            "Time": pd.to_datetime(w["hourly"]["time"][:24]),
            "Temp": w["hourly"]["temperature_2m"][:24]
        }).set_index("Time")
        st.line_chart(df_24h)

    with col_table:
        st.subheader(t["forecast_7d"])
        df_7d = pd.DataFrame({
            "Date": w["daily"]["time"],
            "Max": w["daily"]["temperature_2m_max"],
            "Min": w["daily"]["temperature_2m_min"]
        })
        st.dataframe(df_7d, use_container_width=True)

    if st.button(t["gpt_analysis"]):
        if client:
            with st.spinner("AI Analysis..."):
                prompt = (f"Analyze weather for {loc['name']}. Current temp: {cur['temperature_2m']}C, "
                          f"AQI: {aqi}, Wind: {cur['wind_speed_10m']}m/s. "
                          f"Provide advice for the day in {selected_lang}.")
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.info(response.choices[0].message.content)
        else:
            st.warning(t["no_ai"])

    st.subheader(t["windy_map"])
    layer = st.selectbox(t["map_layer"], ["rain", "wind", "clouds"])
    map_url = f"https://www.windy.com/embed2.html?lat={loc['latitude']}&lon={loc['longitude']}&zoom=6&overlay={layer}"
    st.components.v1.iframe(map_url, height=500)
